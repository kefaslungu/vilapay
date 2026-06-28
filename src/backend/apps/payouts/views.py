from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payouts.models import Payout
from apps.payouts.serializers import PayoutSerializer


class PayoutListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payouts = (
            Payout.objects.filter(recipient=request.user)
            .select_related("cycle__group", "bank_account")
            .order_by("-created_at")
        )
        return Response(PayoutSerializer(payouts, many=True).data)


class PayoutDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            payout = Payout.objects.select_related("cycle__group", "bank_account").get(
                pk=pk, recipient=request.user
            )
        except Payout.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(PayoutSerializer(payout).data)
