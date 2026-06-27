import logging

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import User, UserBankAccount

logger = logging.getLogger(__name__)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "phone_number",
            "password",
            "tier",
            "is_verified",
            "created_at",
        ]
        read_only_fields = ["id", "tier", "is_verified", "created_at"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "phone_number",
            "tier",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "email", "tier", "is_verified", "created_at", "updated_at"]


class UserBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBankAccount
        fields = [
            "id",
            "bank_code",
            "bank_name",
            "account_number",
            "account_name",
            "is_default",
            "verified_at",
            "created_at",
        ]
        read_only_fields = ["id", "bank_name", "account_name", "verified_at", "created_at"]


class AddBankAccountSerializer(serializers.Serializer):
    bank_code = serializers.CharField(max_length=20)
    account_number = serializers.CharField(max_length=20)
