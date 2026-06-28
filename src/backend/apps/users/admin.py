from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserBankAccount


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "full_name", "phone_number", "tier", "is_verified", "is_active", "created_at")
    list_filter = ("tier", "is_verified", "is_active", "is_staff")
    search_fields = ("email", "full_name", "phone_number")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "phone_number", "bvn_hash")}),
        ("Vilapay", {"fields": ("tier", "is_verified", "nomba_customer_id")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "phone_number", "password1", "password2"),
        }),
    )


@admin.register(UserBankAccount)
class UserBankAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "bank_name", "account_number", "account_name", "is_default", "verified_at")
    list_filter = ("bank_name", "is_default")
    search_fields = ("user__email", "account_number", "account_name")
    readonly_fields = ("id", "verified_at", "created_at")
