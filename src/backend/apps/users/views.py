import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import PasswordResetToken, User, UserBankAccount
from apps.users.serializers import (
    AddBankAccountSerializer,
    RegisterSerializer,
    UserBankAccountSerializer,
    UserProfileSerializer,
)
from services.providers import get_payment_provider

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(RegisterSerializer(user).data, status=status.HTTP_201_CREATED)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BankAccountListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = request.user.bank_accounts.order_by("-is_default", "-created_at")
        return Response(UserBankAccountSerializer(accounts, many=True).data)

    def post(self, request):
        serializer = AddBankAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bank_code = serializer.validated_data["bank_code"]
        account_number = serializer.validated_data["account_number"]

        try:
            provider = get_payment_provider()
            nomba_data = provider.verify_bank_account(bank_code, account_number)
        except Exception as exc:
            logger.warning("Bank account verification failed: %s", exc)
            return Response(
                {
                    "detail": "Could not verify account. Check bank code and account number."
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Auto-default the first account added
        is_first = not request.user.bank_accounts.exists()
        account, created = UserBankAccount.objects.get_or_create(
            user=request.user,
            account_number=account_number,
            defaults={
                "bank_code": bank_code,
                "bank_name": nomba_data.get("bankName", ""),
                "account_name": nomba_data.get("accountName", ""),
                "is_default": is_first,
                "verified_at": timezone.now(),
            },
        )
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(UserBankAccountSerializer(account).data, status=response_status)


class BankAccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_account(self, request, pk):
        try:
            return request.user.bank_accounts.get(pk=pk)
        except UserBankAccount.DoesNotExist:
            return None

    def patch(self, request, pk):
        account = self._get_account(request, pk)
        if account is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.data.get("is_default"):
            # Unset all others, then set this one
            request.user.bank_accounts.update(is_default=False)
            account.is_default = True
            account.save(update_fields=["is_default"])

        return Response(UserBankAccountSerializer(account).data)

    def delete(self, request, pk):
        account = self._get_account(request, pk)
        if account is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("current_password", "").strip()
        new_password = request.data.get("new_password", "").strip()

        if not current_password or not new_password:
            return Response(
                {"detail": "current_password and new_password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.check_password(current_password):
            return Response(
                {"detail": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 8:
            return Response(
                {"detail": "New password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(new_password)
        request.user.save(update_fields=["password"])
        logger.info("Password changed for %s", request.user.email)
        return Response({"detail": "Password updated successfully."})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        # Always return 200 — never reveal whether the email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "If that email is registered, a reset link has been sent."}
            )

        token = PasswordResetToken.objects.create(user=user)
        reset_link = (
            f"{settings.VILAPAY_FRONTEND_BASE_URL}/reset-password?token={token.token}"
        )

        send_mail(
            subject="Reset your Vilapay password",
            message=(
                f"Hi {user.full_name},\n\n"
                "We received a request to reset your Vilapay password.\n\n"
                f"Click the link below to set a new password (valid for 24 hours):\n{reset_link}\n\n"
                "If you didn't request this, you can ignore this email — your password won't change.\n\n"
                "— The Vilapay team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Password reset email sent to %s", user.email)
        return Response(
            {"detail": "If that email is registered, a reset link has been sent."}
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_token = request.data.get("token", "").strip()
        new_password = request.data.get("password", "").strip()

        if not raw_token or not new_password:
            return Response(
                {"detail": "token and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 8:
            return Response(
                {"detail": "Password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reset_token = PasswordResetToken.objects.select_related("user").get(
                token=raw_token
            )
        except (PasswordResetToken.DoesNotExist, ValueError):
            return Response(
                {"detail": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not reset_token.is_valid():
            return Response(
                {"detail": "This reset link has expired or already been used."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = reset_token.user
        user.set_password(new_password)
        user.save(update_fields=["password"])

        reset_token.used = True
        reset_token.save(update_fields=["used"])

        logger.info("Password reset successfully for %s", user.email)
        return Response({"detail": "Password updated successfully."})


class BanksListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            provider = get_payment_provider()
            banks = provider.get_banks()
            return Response(banks)
        except Exception as exc:
            logger.warning("Failed to fetch banks list: %s", exc)
            return Response(
                {"detail": "Could not fetch banks list."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
