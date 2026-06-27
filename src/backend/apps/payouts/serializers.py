from rest_framework import serializers

from apps.payouts.models import Payout


class PayoutSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="cycle.group.name", read_only=True)
    cycle_number = serializers.IntegerField(source="cycle.cycle_number", read_only=True)
    bank_account_number = serializers.CharField(
        source="bank_account.account_number", read_only=True
    )
    bank_name = serializers.CharField(source="bank_account.bank_name", read_only=True)

    class Meta:
        model = Payout
        fields = [
            "id",
            "group_name",
            "cycle_number",
            "amount",
            "status",
            "bank_account_number",
            "bank_name",
            "nomba_reference",
            "failure_reason",
            "initiated_at",
            "completed_at",
            "created_at",
        ]
