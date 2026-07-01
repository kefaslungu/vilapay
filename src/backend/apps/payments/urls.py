from django.urls import path

from apps.payments.views import (
    ContributionCheckoutView,
    ContributionListView,
    DirectDebitMandateDetailView,
    DirectDebitMandateListView,
    NombaWebhookView,
)

urlpatterns = [
    path("webhooks/nomba/", NombaWebhookView.as_view(), name="nomba-webhook"),
    path("contributions/", ContributionListView.as_view(), name="contribution-list"),
    path(
        "contributions/checkout/",
        ContributionCheckoutView.as_view(),
        name="contribution-checkout",
    ),
    path("mandates/", DirectDebitMandateListView.as_view(), name="mandate-list"),
    path(
        "mandates/<uuid:pk>/",
        DirectDebitMandateDetailView.as_view(),
        name="mandate-detail",
    ),
]
