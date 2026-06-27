from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
