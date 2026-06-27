from django.urls import path

from apps.wallets.views import WalletDetailView, WalletLedgerView, WalletListView

urlpatterns = [
    path("", WalletListView.as_view(), name="wallet-list"),
    path("<uuid:pk>/", WalletDetailView.as_view(), name="wallet-detail"),
    path("<uuid:pk>/ledger/", WalletLedgerView.as_view(), name="wallet-ledger"),
]
