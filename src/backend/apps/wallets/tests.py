from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


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


class WalletListTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user("user@example.com", "08011111111")
        access = get_access(self.client, self.user.email)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_list_wallets_empty(self):
        """New user has no save-ahead wallets."""
        resp = self.client.get("/v1/wallets/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_list_wallets_unauthenticated(self):
        resp = APIClient().get("/v1/wallets/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
