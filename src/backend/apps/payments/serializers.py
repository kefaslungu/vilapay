from rest_framework import serializers

from apps.payments.models import Contribution


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
