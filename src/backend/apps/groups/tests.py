import datetime
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.groups.models import Group, GroupMembership
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


GROUP_PAYLOAD = {
    "name": "Ajo Friends",
    "slot_count": 3,
    "contribution_amount": "5000.00",
    "frequency": "monthly",
    "start_date": str(datetime.date.today() + datetime.timedelta(days=7)),
}

# Patch target for Nomba VA provisioning called inside activate_group
PROVISION_VA_PATCH = "services.groups._provision_group_va"
# Patch target for wallet VA provisioning (non-fatal, but let's keep tests clean)
WALLET_VA_PATCH = "services.wallets._try_provision_wallet_va"


class CreateGroupTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.creator = make_user("creator@example.com", "08011111111")
        access = get_access(self.client, self.creator.email)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    @patch(WALLET_VA_PATCH)
    def test_create_group_success(self, mock_wallet_va):
        resp = self.client.post("/v1/groups/", GROUP_PAYLOAD)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["name"], GROUP_PAYLOAD["name"])
        self.assertEqual(resp.data["status"], "draft")
        # Creator is automatically added as slot #1
        group = Group.objects.get(id=resp.data["id"])
        self.assertTrue(
            GroupMembership.objects.filter(
                group=group, user=self.creator, slot_number=1
            ).exists()
        )

    def test_create_group_unauthenticated(self):
        resp = APIClient().post("/v1/groups/", GROUP_PAYLOAD)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_group_missing_name(self):
        payload = {**GROUP_PAYLOAD}
        del payload["name"]
        resp = self.client.post("/v1/groups/", payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class JoinGroupTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.creator = make_user("creator@example.com", "08011111111")
        self.member2 = make_user("member2@example.com", "08022222222")
        self.member3 = make_user("member3@example.com", "08033333333")

        # Create a 2-slot group as creator
        creator_client = APIClient()
        access = get_access(creator_client, self.creator.email)
        creator_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        with patch(WALLET_VA_PATCH):
            payload = {**GROUP_PAYLOAD, "slot_count": 2}
            resp = creator_client.post("/v1/groups/", payload)
            self.group_id = resp.data["id"]

    @patch(WALLET_VA_PATCH)
    def test_join_group_success(self, mock_wallet_va):
        client2 = APIClient()
        access = get_access(client2, self.member2.email)
        client2.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        resp = client2.post(f"/v1/groups/{self.group_id}/join/", {})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["slot_number"], 2)

    @patch(WALLET_VA_PATCH)
    def test_join_already_member(self, mock_wallet_va):
        # Creator tries to join their own group again
        creator_client = APIClient()
        access = get_access(creator_client, self.creator.email)
        creator_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        resp = creator_client.post(f"/v1/groups/{self.group_id}/join/", {})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already a member", resp.data["detail"])

    @patch(WALLET_VA_PATCH)
    def test_join_full_group_returns_400(self, mock_wallet_va):
        # Fill the second slot
        client2 = APIClient()
        access2 = get_access(client2, self.member2.email)
        client2.credentials(HTTP_AUTHORIZATION=f"Bearer {access2}")
        client2.post(f"/v1/groups/{self.group_id}/join/", {})

        # Third member tries to join — group is full
        client3 = APIClient()
        access3 = get_access(client3, self.member3.email)
        client3.credentials(HTTP_AUTHORIZATION=f"Bearer {access3}")

        resp = client3.post(f"/v1/groups/{self.group_id}/join/", {})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_join_nonexistent_group(self):
        import uuid

        client2 = APIClient()
        access = get_access(client2, self.member2.email)
        client2.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        resp = client2.post(f"/v1/groups/{uuid.uuid4()}/join/", {})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class ActivateGroupTest(TestCase):
    def setUp(self):
        self.creator = make_user("creator@example.com", "08011111111")
        self.member2 = make_user("member2@example.com", "08022222222")

        creator_client = APIClient()
        access = get_access(creator_client, self.creator.email)
        creator_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        with patch(WALLET_VA_PATCH):
            payload = {**GROUP_PAYLOAD, "slot_count": 2}
            resp = creator_client.post("/v1/groups/", payload)
            self.group_id = resp.data["id"]

        # Member 2 joins
        client2 = APIClient()
        access2 = get_access(client2, self.member2.email)
        client2.credentials(HTTP_AUTHORIZATION=f"Bearer {access2}")
        with patch(WALLET_VA_PATCH):
            client2.post(f"/v1/groups/{self.group_id}/join/", {})

        self.creator_client = APIClient()
        creator_access = get_access(self.creator_client, self.creator.email)
        self.creator_client.credentials(HTTP_AUTHORIZATION=f"Bearer {creator_access}")

    @patch(PROVISION_VA_PATCH)
    def test_activate_group_success(self, mock_provision):
        """Creator can activate a fully-filled group."""
        mock_provision.return_value = None  # No-op: skip Nomba call
        resp = self.creator_client.post(f"/v1/groups/{self.group_id}/activate/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], "active")

    @patch(PROVISION_VA_PATCH)
    def test_activate_group_non_creator_forbidden(self, mock_provision):
        """Non-creator gets 403."""
        client2 = APIClient()
        access2 = get_access(client2, self.member2.email)
        client2.credentials(HTTP_AUTHORIZATION=f"Bearer {access2}")

        resp = client2.post(f"/v1/groups/{self.group_id}/activate/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_activate_group_not_full_returns_400(self):
        """Cannot activate if slots are not all filled."""
        # Create a fresh group with 3 slots (only creator in slot 1)
        creator_client = APIClient()
        access = get_access(creator_client, self.creator.email)
        creator_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        with patch(WALLET_VA_PATCH):
            resp = creator_client.post(
                "/v1/groups/", {**GROUP_PAYLOAD, "slot_count": 3}
            )
        new_group_id = resp.data["id"]

        resp = self.creator_client.post(f"/v1/groups/{new_group_id}/activate/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class CancelGroupTest(TestCase):
    def setUp(self):
        self.creator = make_user("creator@example.com", "08011111111")
        self.other = make_user("other@example.com", "08022222222")

        creator_client = APIClient()
        access = get_access(creator_client, self.creator.email)
        creator_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        with patch(WALLET_VA_PATCH):
            resp = creator_client.post("/v1/groups/", GROUP_PAYLOAD)
            self.group_id = resp.data["id"]

        self.creator_client = APIClient()
        creator_access = get_access(self.creator_client, self.creator.email)
        self.creator_client.credentials(HTTP_AUTHORIZATION=f"Bearer {creator_access}")

    def test_cancel_group_success(self):
        resp = self.creator_client.post(f"/v1/groups/{self.group_id}/cancel/", {})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], "cancelled")

    def test_cancel_group_non_creator_forbidden(self):
        other_client = APIClient()
        access = get_access(other_client, self.other.email)
        other_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        resp = other_client.post(f"/v1/groups/{self.group_id}/cancel/", {})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_already_cancelled(self):
        self.creator_client.post(f"/v1/groups/{self.group_id}/cancel/", {})
        resp = self.creator_client.post(f"/v1/groups/{self.group_id}/cancel/", {})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class ListGroupsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user("user@example.com", "08011111111")
        access = get_access(self.client, self.user.email)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    @patch(WALLET_VA_PATCH)
    def test_list_only_my_groups(self, mock_wallet_va):
        # Create one group as this user
        self.client.post("/v1/groups/", GROUP_PAYLOAD)

        # Create another group as a different user — should not appear in response
        other = make_user("other@example.com", "08022222222")
        other_client = APIClient()
        access = get_access(other_client, other.email)
        other_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        other_client.post("/v1/groups/", {**GROUP_PAYLOAD, "name": "Other Group"})

        resp = self.client.get("/v1/groups/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [g["name"] for g in resp.data]
        self.assertIn(GROUP_PAYLOAD["name"], names)
        self.assertNotIn("Other Group", names)
