from django.contrib import admin

from .models import LedgerEntry, SaveAheadWallet


class LedgerEntryInline(admin.TabularInline):
    model = LedgerEntry
    extra = 0
    readonly_fields = ("id", "entry_type", "amount", "balance_after", "description", "nomba_transaction_ref", "created_at")
    fields = ("entry_type", "amount", "balance_after", "description", "nomba_transaction_ref", "created_at")
    can_delete = False


@admin.register(SaveAheadWallet)
class SaveAheadWalletAdmin(admin.ModelAdmin):
    list_display = ("user", "membership", "balance", "nomba_virtual_account_number", "created_at")
    search_fields = ("user__email", "membership__group__name", "nomba_virtual_account_number")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [LedgerEntryInline]


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("entry_type", "amount", "balance_after", "group", "wallet", "nomba_transaction_ref", "created_at")
    list_filter = ("entry_type",)
    search_fields = ("nomba_transaction_ref", "group__name", "wallet__user__email")
    readonly_fields = ("id", "created_at")
    # Ledger is immutable — no delete
    def has_delete_permission(self, request, obj=None):
        return False
