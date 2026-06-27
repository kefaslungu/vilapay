from django.urls import path

from apps.payouts.views import PayoutDetailView, PayoutListView

urlpatterns = [
    path("", PayoutListView.as_view(), name="payout-list"),
    path("<uuid:pk>/", PayoutDetailView.as_view(), name="payout-detail"),
]
