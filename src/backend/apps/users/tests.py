from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


def make_user(email="alice@example.com", phone="08011111111", password="Pass1234!"):
    return User.objects.create_user(
        email=email,
        password=password,
        full_name="Alice Test",
        phone_number=phone,
    )


def get_tokens(client, email, password):
    resp = client.post("/v1/auth/login/", {"email": email, "password": password})
    return resp.data.get("access"), resp.data.get("refresh")


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/v1/auth/register/"
        self.valid_payload = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "phone_number": "08099999999",
            "password": "StrongPass1!",
        }

    def test_register_success(self):
        resp = self.client.post(self.url, self.valid_payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", resp.data)
        self.assertEqual(resp.data["email"], self.valid_payload["email"])
        self.assertTrue(User.objects.filter(email=self.valid_payload["email"]).exists())

    def test_register_duplicate_email(self):
        make_user(email=self.valid_payload["email"], phone="08033333333")
        resp = self.client.post(self.url, self.valid_payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_required_fields(self):
        resp = self.client.post(self.url, {"email": "x@x.com"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        payload = {**self.valid_payload, "password": "123"}
        resp = self.client.post(self.url, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/v1/auth/login/"
        self.password = "Pass1234!"
        self.user = make_user(password=self.password)

    def test_login_success_returns_tokens(self):
        resp = self.client.post(self.url, {"email": self.user.email, "password": self.password})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_login_wrong_password(self):
        resp = self.client.post(self.url, {"email": self.user.email, "password": "wrongpass"})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_email(self):
        resp = self.client.post(self.url, {"email": "nobody@example.com", "password": "Pass1234!"})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = "Pass1234!"
        self.user = make_user(password=self.password)
        access, _ = get_tokens(self.client, self.user.email, self.password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_get_profile_authenticated(self):
        resp = self.client.get("/v1/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["email"], self.user.email)
        self.assertIn("tier", resp.data)
        self.assertIn("is_verified", resp.data)

    def test_get_profile_unauthenticated(self):
        unauth = APIClient()
        resp = unauth.get("/v1/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
