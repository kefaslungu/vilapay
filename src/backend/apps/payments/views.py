import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.models import Contribution
from apps.payments.serializers import ContributionSerializer
from services.exceptions import WebhookVerificationError
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
