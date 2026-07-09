import base64
import hashlib
import hmac
from datetime import UTC, datetime

import requests
from django.conf import settings
from django.core.cache import cache

from .base import BasePaymentProvider

# Default timeout for all Nomba API calls (connect, read).
# Transfers use a longer read timeout because Nomba may take extra time
# to process them. Override via NOMBA_REQUEST_TIMEOUT in settings if needed.
_DEFAULT_TIMEOUT = getattr(settings, "NOMBA_REQUEST_TIMEOUT", (10, 30))
_TRANSFER_TIMEOUT = getattr(settings, "NOMBA_TRANSFER_TIMEOUT", (10, 60))


class NombaProvider(BasePaymentProvider):
    def __init__(self):
        self.base_url = settings.NOMBA_BASE_URL
        self.client_id = settings.NOMBA_CLIENT_ID
        self.client_secret = settings.NOMBA_CLIENT_SECRET
        self.account_id = settings.NOMBA_ACCOUNT_ID

    def get_access_token(self):
        token = cache.get("nomba_access_token")
        if token:
            return token

        headers = {"Content-Type": "application/json"}
        if self.account_id:
            headers["accountId"] = self.account_id

        response = requests.post(
            f"{self.base_url}/auth/token/issue",
            json={
                "clientId": self.client_id,
                "clientSecret": self.client_secret,
                "grantType": "client_credentials",
            },
            headers=headers,
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()["data"]
        token = data["access_token"]

        # Cache until 30 minutes before the token actually expires,
        # as recommended by Nomba. Falls back to 55 min if expiresAt is absent.
        ttl = 55 * 60
        expires_at = data.get("expiresAt")
        if expires_at:
            expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            seconds_left = (expiry - datetime.now(UTC)).total_seconds()
            ttl = max(int(seconds_left) - 30 * 60, 60)  # at least 60 s

        cache.set("nomba_access_token", token, ttl)
        return token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.get_access_token()}",
            "accountId": self.account_id,
            "Content-Type": "application/json",
        }

    def create_virtual_account(
        self, account_ref, account_name, sub_account_id=None, **kwargs
    ):
        if sub_account_id:
            url = f"{self.base_url}/accounts/virtual/{sub_account_id}"
        else:
            url = f"{self.base_url}/accounts/virtual"

        response = requests.post(
            url,
            json={
                "accountRef": account_ref,
                "accountName": account_name,
                **kwargs,
            },
            headers=self._headers(),
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        body = response.json()
        if "data" not in body:
            raise ValueError(f"Unexpected Nomba response (no data key): {body}")
        return body["data"]

    def get_virtual_account(self, account_id):
        response = requests.get(
            f"{self.base_url}/accounts/virtual/{account_id}",
            headers=self._headers(),
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["data"]

    def transfer_to_bank(self, bank_code, account_number, amount, narration, reference):
        response = requests.post(
            f"{self.base_url}/transfers/initiate",
            json={
                "amount": str(amount),
                "bankCode": bank_code,
                "accountNumber": account_number,
                "narration": narration,
                "merchantTxRef": reference,
                "currency": "NGN",
            },
            headers=self._headers(),
            timeout=_TRANSFER_TIMEOUT,  # longer timeout for financial transfers
        )
        response.raise_for_status()
        return response.json()["data"]

    def verify_bank_account(self, bank_code, account_number):
        response = requests.post(
            f"{self.base_url}/transfers/account/lookup",
            json={"bankCode": bank_code, "accountNumber": account_number},
            headers=self._headers(),
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["data"]

    def get_banks(self):
        response = requests.get(
            f"{self.base_url}/transfers/banks",
            headers=self._headers(),
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["data"]

    def create_direct_debit_mandate(
        self, customer_data, amount, frequency, start_date, end_date
    ):
        response = requests.post(
            f"{self.base_url}/direct-debit/mandate",
            json={
                **customer_data,
                "amount": str(amount),
                "frequencyType": frequency,
                "startDate": start_date,
                "endDate": end_date,
            },
            headers=self._headers(),
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["data"]

    def create_checkout_order(
        self, order_reference, customer_email, amount, customer_id=None, redirect_url=None
    ):
        order_payload = {
            "orderReference": order_reference,
            "customerId": customer_id or customer_email,
            "customerEmail": customer_email,
            "amount": str(amount),
            "currency": "NGN",
            "accountId": self.account_id,
            "callbackUrl": f"{settings.VILAPAY_API_BASE_URL}/v1/payments/webhooks/nomba/",
        }
        if redirect_url:
            order_payload["redirectUrl"] = redirect_url

        response = requests.post(
            f"{self.base_url}/checkout/order",
            json={"order": order_payload},
            headers=self._headers(),
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        body = response.json()
        if "data" not in body:
            raise ValueError(f"Unexpected Nomba response (no data key): {body}")
        return body["data"]

    def charge_tokenized_card(self, token_key, amount, reference, customer_id):
        response = requests.post(
            f"{self.base_url}/checkout/tokenized-card-payment",
            json={
                "tokenKey": token_key,
                "order": {
                    "orderReference": reference,
                    "customerId": customer_id,
                    "amount": str(amount),
                    "currency": "NGN",
                    "accountId": self.account_id,
                    "callbackUrl": f"{settings.VILAPAY_API_BASE_URL}/v1/payments/webhooks/nomba/",
                },
            },
            headers=self._headers(),
            timeout=_TRANSFER_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["data"]

    def get_transaction(self, transaction_ref):
        response = requests.get(
            f"{self.base_url}/transactions/{transaction_ref}",
            headers=self._headers(),
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["data"]

    def verify_webhook(self, data: dict, signature: str) -> bool:
        """
        Verify a Nomba webhook signature.
        Nomba signs: event_type:requestId:userId:walletId:transactionId:
                     transactionType:transactionTime:responseCode:timestamp
        Algorithm: HMAC-SHA256, Base64-encoded.
        """
        secret = getattr(settings, "NOMBA_WEBHOOK_SECRET", "")
        fields = [
            data.get("eventType") or data.get("event", ""),
            data.get("requestId", ""),
            data.get("userId", ""),
            data.get("walletId", ""),
            data.get("transactionId", ""),
            data.get("transactionType", ""),
            data.get("transactionTime", ""),
            data.get("responseCode", ""),
            data.get("timestamp", ""),
        ]
        payload_str = ":".join(str(f) for f in fields)
        mac = hmac.new(secret.encode(), payload_str.encode(), hashlib.sha256)
        expected = base64.b64encode(mac.digest()).decode()
        return hmac.compare_digest(expected, signature)
