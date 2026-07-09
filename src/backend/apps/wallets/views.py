from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.models import Contribution
from apps.payouts.models import Payout
from apps.wallets.models import LedgerEntry, SaveAheadWallet
from apps.wallets.serializers import LedgerEntrySerializer, SaveAheadWalletSerializer


class WalletListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallets = request.user.save_ahead_wallets.select_related(
            "membership__group"
        ).order_by("-created_at")
        return Response(SaveAheadWalletSerializer(wallets, many=True).data)


class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            wallet = request.user.save_ahead_wallets.select_related(
                "membership__group"
            ).get(pk=pk)
        except SaveAheadWallet.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(SaveAheadWalletSerializer(wallet).data)


class WalletLedgerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            wallet = request.user.save_ahead_wallets.get(pk=pk)
        except SaveAheadWallet.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        entries = LedgerEntry.objects.filter(wallet=wallet).order_by("-created_at")
        return Response(LedgerEntrySerializer(entries, many=True).data)


class TransactionListView(APIView):
    """
    Returns a unified, chronologically sorted list of the user's
    contributions and payouts for the transaction history screen.

    GET /v1/wallets/transactions/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_map = {
            "completed": "success",
            "failed": "failed",
            "pending": "pending",
            "processing": "pending",
        }

        contributions = (
            Contribution.objects.filter(member__user=request.user)
            .select_related("cycle__group")
            .order_by("-created_at")
        )
        payouts = (
            Payout.objects.filter(cycle__group__memberships__user=request.user)
            .select_related("cycle__group")
            .distinct()
            .order_by("-created_at")
        )

        transactions = []

        for c in contributions:
            transactions.append({
                "id": str(c.id),
                "amount": str(c.amount),
                "transaction_type": "contribution",
                "status": status_map.get(c.status, "pending"),
                "group_name": c.cycle.group.name,
                "created_at": c.created_at.isoformat(),
            })

        for p in payouts:
            transactions.append({
                "id": str(p.id),
                "amount": str(p.amount),
                "transaction_type": "payout",
                "status": status_map.get(p.status, "pending"),
                "group_name": p.cycle.group.name,
                "created_at": p.created_at.isoformat(),
            })

        transactions.sort(key=lambda x: x["created_at"], reverse=True)

        return Response(transactions)
