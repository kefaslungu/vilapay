from decimal import Decimal

from rest_framework import serializers

from apps.groups.models import Group, GroupCycle, GroupMembership


class GroupMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = GroupMembership
        fields = [
            "id",
            "user_email",
            "user_name",
            "slot_number",
            "status",
            "joined_at",
        ]


class GroupCycleSerializer(serializers.ModelSerializer):
    recipient_slot = serializers.IntegerField(source="recipient.slot_number", read_only=True)
    recipient_name = serializers.CharField(
        source="recipient.user.full_name", read_only=True
    )

    class Meta:
        model = GroupCycle
        fields = [
            "id",
            "cycle_number",
            "recipient_slot",
            "recipient_name",
            "start_date",
            "end_date",
            "payout_date",
            "status",
            "total_collected",
        ]


class GroupSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    pot_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    member_count = serializers.SerializerMethodField()
    virtual_account = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "created_by_email",
            "slot_count",
            "contribution_amount",
            "pot_amount",
            "frequency",
            "start_date",
            "status",
            "current_cycle",
            "member_count",
            "virtual_account",
            "created_at",
            "updated_at",
        ]

    def get_member_count(self, obj):
        return obj.memberships.filter(status=GroupMembership.Status.ACTIVE).count()

    def get_virtual_account(self, obj):
        if not obj.nomba_virtual_account_number:
            return None
        return {
            "account_number": obj.nomba_virtual_account_number,
            "bank_name": obj.nomba_virtual_account_bank,
        }


class CreateGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    slot_count = serializers.IntegerField(min_value=2, max_value=50)
    contribution_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("100.00")
    )
    frequency = serializers.ChoiceField(choices=Group.Frequency.choices)
    start_date = serializers.DateField()


class JoinGroupSerializer(serializers.Serializer):
    slot_number = serializers.IntegerField(required=False, min_value=1)


class CancelGroupSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
