import hashlib
import hmac

import requests
from django.conf import settings
from django.core.cache import cache

from .base import BasePaymentProvider


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
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()["data"]
        token = data["access_token"]
        # expiresAt is an ISO timestamp; cache for 55 minutes as a safe default
        cache.set("nomba_access_token", token, 55 * 60)
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
        )
        response.raise_for_status()
        return response.json()["data"]

    def get_virtual_account(self, account_id):
        response = requests.get(
            f"{self.base_url}/accounts/virtual/{account_id}", headers=self._headers()
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
        )
        response.raise_for_status()
        return response.json()["data"]

    def verify_bank_account(self, bank_code, account_number):
        response = requests.post(
            f"{self.base_url}/transfers/account/lookup",
            json={"bankCode": bank_code, "accountNumber": account_number},
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()["data"]

    def get_banks(self):
        response = requests.get(
            f"{self.base_url}/transfers/banks", headers=self._headers()
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
        )
        response.raise_for_status()
        return response.json()["data"]

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
                    "callbackUrl": f"{settings.ALLOWED_HOSTS[0]}/api/payments/webhooks/nomba/",
                },
            },
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()["data"]

    def get_transaction(self, transaction_ref):
        response = requests.get(
            f"{self.base_url}/transactions/{transaction_ref}", headers=self._headers()
        )
        response.raise_for_status()
        return response.json()["data"]

    def verify_webhook(self, payload, signature):
        secret = getattr(settings, "NOMBA_WEBHOOK_SECRET", "")
        expected = hmac.new(secret.encode(), payload, hashlib.sha512).hexdigest()
        return hmac.compare_digest(expected, signature)
