import json
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from services.exceptions import WebhookVerificationError


def make_user(email, phone, password="Pass1234!"):
    return User.objects.create_user(
        email=email,
        password=password,
        full_name="Test User",
        phone_number=phone,
    )


def get_access(client, email, password="Pass1234!"):
    resp = client.post("/v1/auth/login/", {"email": email, "password": password})
    return resp.data["access"]


class NombaWebhookTest(TestCase):
    URL = "/v1/payments/webhooks/nomba/"

    def test_invalid_signature_returns_400(self):
        """Any request with a signature that fails HMAC check gets a 400."""
        with patch(
            "apps.payments.views.handle_nomba_webhook",
            side_effect=WebhookVerificationError("bad sig"),
        ):
            resp = self.client.post(
                self.URL,
                data=json.dumps({"event": "virtualaccount.credit"}),
                content_type="application/json",
                HTTP_X_NOMBA_SIGNATURE="invalidsig",
            )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid signature", resp.data["detail"])

    def test_valid_webhook_returns_200(self):
        """Valid webhook (mocked) returns 200 with handler result."""
        with patch(
            "apps.payments.views.handle_nomba_webhook",
            return_value={"status": "ok", "type": "contribution_recorded"},
        ):
            resp = self.client.post(
                self.URL,
                data=json.dumps({"event": "virtualaccount.credit", "data": {}}),
                content_type="application/json",
                HTTP_X_NOMBA_SIGNATURE="validsig",
            )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], "ok")

    def test_processing_error_still_returns_200(self):
        """Unexpected processing errors return 200 (so Nomba doesn't retry)."""
        with patch(
            "apps.payments.views.handle_nomba_webhook",
            side_effect=RuntimeError("unexpected"),
        ):
            resp = self.client.post(
                self.URL,
                data=json.dumps({"event": "virtualaccount.credit"}),
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class ContributionListTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user("user@example.com", "08011111111")
        access = get_access(self.client, self.user.email)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_list_contributions_empty(self):
        resp = self.client.get("/v1/payments/contributions/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_list_contributions_unauthenticated(self):
        resp = APIClient().get("/v1/payments/contributions/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
