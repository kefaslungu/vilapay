from django.urls import path

from apps.wallets.views import (
    TransactionListView,
    WalletDetailView,
    WalletLedgerView,
    WalletListView,
    WalletSummaryView,
)

urlpatterns = [
    path("", WalletListView.as_view(), name="wallet-list"),
    path("me/", WalletSummaryView.as_view(), name="wallet-summary"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path("<uuid:pk>/", WalletDetailView.as_view(), name="wallet-detail"),
    path("<uuid:pk>/ledger/", WalletLedgerView.as_view(), name="wallet-ledger"),
]
