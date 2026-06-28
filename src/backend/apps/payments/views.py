import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.groups.models import GroupMembership
from apps.payments.models import Contribution, DirectDebitMandate
from apps.payments.serializers import (
    ContributionSerializer,
    CreateMandateSerializer,
    DirectDebitMandateSerializer,
)
from apps.users.models import UserBankAccount
from services.exceptions import WebhookVerificationError
from services.providers import get_payment_provider
from services.webhooks import handle_nomba_webhook

logger = logging.getLogger(__name__)


class NombaWebhookView(APIView):
    """
    Receives Nomba webhook events.

    No authentication — Nomba signs each request with HMAC-SHA512.
    Signature verification happens inside handle_nomba_webhook.

    We return 200 for all processing errors (after logging) so that
    Nomba does not retry events that we have already received.
    Only invalid signatures get a 400 response.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Access raw body before DRF parsers can consume the stream
        payload = request.body
        signature = request.META.get("HTTP_X_NOMBA_SIGNATURE", "")

        try:
            result = handle_nomba_webhook(payload, signature)
            return Response(result, status=status.HTTP_200_OK)
        except WebhookVerificationError:
            logger.warning("Nomba webhook: invalid signature received")
            return Response(
                {"detail": "Invalid signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Unexpected error processing Nomba webhook")
            # Return 200 so Nomba does not retry — error is captured in logs
            return Response({"status": "error"}, status=status.HTTP_200_OK)


class ContributionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contributions = (
            Contribution.objects.filter(member__user=request.user)
            .select_related("cycle__group")
            .order_by("-created_at")
        )
        return Response(ContributionSerializer(contributions, many=True).data)


class DirectDebitMandateListView(APIView):
    """List all direct debit mandates for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        mandates = (
            DirectDebitMandate.objects.filter(membership__user=request.user)
            .select_related("membership__group")
            .order_by("-created_at")
        )
        return Response(DirectDebitMandateSerializer(mandates, many=True).data)

    def post(self, request):
        """Create a new direct debit mandate for a group membership."""
        serializer = CreateMandateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        membership_id = serializer.validated_data["membership_id"]
        bank_account_id = serializer.validated_data["bank_account_id"]

        # Verify membership belongs to the user
        try:
            membership = GroupMembership.objects.select_related("group").get(
                id=membership_id, user=request.user, status=GroupMembership.Status.ACTIVE
            )
        except GroupMembership.DoesNotExist:
            return Response(
                {"detail": "Active membership not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify bank account belongs to the user
        try:
            bank_account = UserBankAccount.objects.get(id=bank_account_id, user=request.user)
        except UserBankAccount.DoesNotExist:
            return Response(
                {"detail": "Bank account not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        group = membership.group

        # Prevent duplicate active mandates for the same membership
        if DirectDebitMandate.objects.filter(
            membership=membership, status__in=[DirectDebitMandate.Status.PENDING, DirectDebitMandate.Status.ACTIVE]
        ).exists():
            return Response(
                {"detail": "An active mandate already exists for this membership."},
                status=status.HTTP_409_CONFLICT,
            )

        provider = get_payment_provider()
        customer_data = {
            "accountNumber": bank_account.account_number,
            "bankCode": bank_account.bank_code,
            "accountName": bank_account.account_name,
        }

        try:
            result = provider.create_direct_debit_mandate(
                customer_data=customer_data,
                amount=group.contribution_amount,
                frequency=group.frequency,
                start_date=str(group.start_date),
                end_date=str(group.start_date.replace(year=group.start_date.year + 5)),
            )
        except Exception:
            logger.exception("Failed to create Nomba direct debit mandate")
            return Response(
                {"detail": "Could not create mandate with payment provider. Try again later."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        mandate = DirectDebitMandate.objects.create(
            membership=membership,
            nomba_mandate_id=result.get("mandateId", ""),
            status=DirectDebitMandate.Status.PENDING,
            amount=group.contribution_amount,
            frequency=group.frequency,
            start_date=group.start_date,
            end_date=group.start_date.replace(year=group.start_date.year + 5),
        )

        return Response(
            DirectDebitMandateSerializer(mandate).data,
            status=status.HTTP_201_CREATED,
        )


class DirectDebitMandateDetailView(APIView):
    """Cancel a specific direct debit mandate."""

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return DirectDebitMandate.objects.select_related("membership__group").get(
                id=pk, membership__user=user
            )
        except DirectDebitMandate.DoesNotExist:
            return None

    def get(self, request, pk):
        mandate = self.get_object(pk, request.user)
        if not mandate:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(DirectDebitMandateSerializer(mandate).data)

    def delete(self, request, pk):
        mandate = self.get_object(pk, request.user)
        if not mandate:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if mandate.status == DirectDebitMandate.Status.CANCELLED:
            return Response(
                {"detail": "Mandate is already cancelled."},
                status=status.HTTP_409_CONFLICT,
            )

        mandate.status = DirectDebitMandate.Status.CANCELLED
        mandate.save(update_fields=["status", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
