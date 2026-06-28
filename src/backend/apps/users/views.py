import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import UserBankAccount
from apps.users.serializers import (
    AddBankAccountSerializer,
    RegisterSerializer,
    UserBankAccountSerializer,
    UserProfileSerializer,
)
from services.providers import get_payment_provider

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(RegisterSerializer(user).data, status=status.HTTP_201_CREATED)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BankAccountListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = request.user.bank_accounts.order_by("-is_default", "-created_at")
        return Response(UserBankAccountSerializer(accounts, many=True).data)

    def post(self, request):
        serializer = AddBankAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bank_code = serializer.validated_data["bank_code"]
        account_number = serializer.validated_data["account_number"]

        try:
            provider = get_payment_provider()
            nomba_data = provider.verify_bank_account(bank_code, account_number)
        except Exception as exc:
            logger.warning("Bank account verification failed: %s", exc)
            return Response(
                {
                    "detail": "Could not verify account. Check bank code and account number."
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Auto-default the first account added
        is_first = not request.user.bank_accounts.exists()
        account, created = UserBankAccount.objects.get_or_create(
            user=request.user,
            account_number=account_number,
            defaults={
                "bank_code": bank_code,
                "bank_name": nomba_data.get("bankName", ""),
                "account_name": nomba_data.get("accountName", ""),
                "is_default": is_first,
                "verified_at": timezone.now(),
            },
        )
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(UserBankAccountSerializer(account).data, status=response_status)


class BankAccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_account(self, request, pk):
        try:
            return request.user.bank_accounts.get(pk=pk)
        except UserBankAccount.DoesNotExist:
            return None

    def patch(self, request, pk):
        account = self._get_account(request, pk)
        if account is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.data.get("is_default"):
            # Unset all others, then set this one
            request.user.bank_accounts.update(is_default=False)
            account.is_default = True
            account.save(update_fields=["is_default"])

        return Response(UserBankAccountSerializer(account).data)

    def delete(self, request, pk):
        account = self._get_account(request, pk)
        if account is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BanksListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            provider = get_payment_provider()
            banks = provider.get_banks()
            return Response(banks)
        except Exception as exc:
            logger.warning("Failed to fetch banks list: %s", exc)
            return Response(
                {"detail": "Could not fetch banks list."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
