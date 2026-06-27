from django.urls import path

from apps.payments.views import ContributionListView, NombaWebhookView

urlpatterns = [
    path("webhooks/nomba/", NombaWebhookView.as_view(), name="nomba-webhook"),
    path("contributions/", ContributionListView.as_view(), name="contribution-list"),
]
