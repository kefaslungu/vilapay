from rest_framework import serializers

from apps.payments.models import Contribution, DirectDebitMandate


class ContributionSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="cycle.group.name", read_only=True)
    cycle_number = serializers.IntegerField(source="cycle.cycle_number", read_only=True)

    class Meta:
        model = Contribution
        fields = [
            "id",
            "group_name",
            "cycle_number",
            "amount",
            "status",
            "payment_method",
            "nomba_reference",
            "paid_at",
            "created_at",
        ]


class DirectDebitMandateSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="membership.group.name", read_only=True)
    slot_number = serializers.IntegerField(source="membership.slot_number", read_only=True)

    class Meta:
        model = DirectDebitMandate
        fields = [
            "id",
            "group_name",
            "slot_number",
            "nomba_mandate_id",
            "status",
            "amount",
            "frequency",
            "start_date",
            "end_date",
            "created_at",
        ]


class CreateMandateSerializer(serializers.Serializer):
    membership_id = serializers.UUIDField()
    bank_account_id = serializers.UUIDField()
