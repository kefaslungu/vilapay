from rest_framework import serializers

from apps.wallets.models import LedgerEntry, SaveAheadWallet


class SaveAheadWalletSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="membership.group.name", read_only=True)
    group_id = serializers.UUIDField(source="membership.group.id", read_only=True)
    slot_number = serializers.IntegerField(
        source="membership.slot_number", read_only=True
    )
    virtual_account = serializers.SerializerMethodField()

    class Meta:
        model = SaveAheadWallet
        fields = [
            "id",
            "group_id",
            "group_name",
            "slot_number",
            "balance",
            "virtual_account",
            "created_at",
            "updated_at",
        ]

    def get_virtual_account(self, obj):
        if not obj.nomba_virtual_account_number:
            return None
        return {
            "account_number": obj.nomba_virtual_account_number,
            "bank_name": obj.nomba_virtual_account_bank,
        }


class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = [
            "id",
            "entry_type",
            "amount",
            "balance_after",
            "description",
            "nomba_transaction_ref",
            "created_at",
        ]
