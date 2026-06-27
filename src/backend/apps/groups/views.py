import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.groups.models import Group, GroupMembership
from apps.groups.serializers import (
    CancelGroupSerializer,
    CreateGroupSerializer,
    GroupCycleSerializer,
    GroupMembershipSerializer,
    GroupSerializer,
    JoinGroupSerializer,
)
from services.exceptions import (
    GroupFullError,
    InvalidGroupStateError,
    PaymentProviderError,
    SlotTakenError,
)
from services.groups import activate_group, cancel_group, create_group, join_group

logger = logging.getLogger(__name__)


class GroupListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership_group_ids = GroupMembership.objects.filter(
            user=request.user, status=GroupMembership.Status.ACTIVE
        ).values_list("group_id", flat=True)
        groups = Group.objects.filter(id__in=membership_group_ids).select_related(
            "created_by"
        )
        return Response(GroupSerializer(groups, many=True).data)

    def post(self, request):
        serializer = CreateGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        group = create_group(
            creator=request.user,
            name=d["name"],
            slot_count=d["slot_count"],
            contribution_amount=d["contribution_amount"],
            frequency=d["frequency"],
            start_date=d["start_date"],
        )
        # Auto-create a save-ahead wallet for the creator (slot #1) — non-fatal
        try:
            from services.wallets import create_wallet

            membership = group.memberships.get(user=request.user)
            create_wallet(membership)
        except Exception:
            logger.warning(
                "Wallet creation failed for group creator %s", request.user.email
            )

        return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)


class GroupDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            group = Group.objects.select_related("created_by").get(pk=pk)
        except Group.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(GroupSerializer(group).data)


class JoinGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if group.memberships.filter(
            user=request.user, status=GroupMembership.Status.ACTIVE
        ).exists():
            return Response(
                {"detail": "You are already a member of this group."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = JoinGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            membership = join_group(
                group=group,
                user=request.user,
                slot_number=serializer.validated_data.get("slot_number"),
            )
        except (GroupFullError, SlotTakenError, InvalidGroupStateError, ValueError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Auto-create save-ahead wallet — non-fatal if it fails
        try:
            from services.wallets import create_wallet

            create_wallet(membership)
        except Exception:
            logger.warning(
                "Wallet creation failed for membership %s — continuing", membership.id
            )

        return Response(
            GroupMembershipSerializer(membership).data, status=status.HTTP_201_CREATED
        )


class ActivateGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if group.created_by_id != request.user.id:
            return Response(
                {"detail": "Only the group creator can activate this group."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            group = activate_group(group)
        except InvalidGroupStateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except PaymentProviderError as exc:
            logger.error("VA provisioning failed for group %s: %s", pk, exc)
            return Response(
                {"detail": "Payment provider error. Please try again later."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(GroupSerializer(group).data)


class CancelGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if group.created_by_id != request.user.id:
            return Response(
                {"detail": "Only the group creator can cancel this group."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CancelGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            group = cancel_group(
                group, reason=serializer.validated_data.get("reason", "")
            )
        except InvalidGroupStateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(GroupSerializer(group).data)


class GroupMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        members = group.memberships.select_related("user").order_by("slot_number")
        return Response(GroupMembershipSerializer(members, many=True).data)


class GroupCyclesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        cycles = group.cycles.select_related("recipient__user").order_by("cycle_number")
        return Response(GroupCycleSerializer(cycles, many=True).data)
