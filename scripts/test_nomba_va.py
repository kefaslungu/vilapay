#!/usr/bin/env python
"""Test Nomba virtual account creation in sandbox."""
import os
import sys
import uuid

import requests
from decouple import Config, RepositoryEnv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
config = Config(RepositoryEnv(env_path))

NOMBA_BASE_URL = "https://sandbox.nomba.com/v1"
CLIENT_ID = config("TEST_CLIENT_ID")
CLIENT_SECRET = config("TEST_PRIVATE_KEY")
ACCOUNT_ID = config("NOMBA_ACCOUNT_ID", default="")

# ── Step 1: Authenticate ──────────────────────────────────────────────────────
print("Step 1: Authenticating...")

auth_headers = {"Content-Type": "application/json"}
if ACCOUNT_ID:
    auth_headers["accountId"] = ACCOUNT_ID

auth_response = requests.post(
    f"{NOMBA_BASE_URL}/auth/token/issue",
    json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    },
    headers=auth_headers,
)

print(f"Auth status: {auth_response.status_code}")

if auth_response.status_code != 200:
    print(f"Auth failed: {auth_response.text}")
    sys.exit(1)

auth_data = auth_response.json()["data"]
access_token = auth_data["access_token"]
print(f"Token: {access_token[:20]}...")
print()

# ── Step 2: Create virtual account ────────────────────────────────────────────
print("Step 2: Creating virtual account...")

# Use a unique accountRef to avoid duplicate conflicts on re-runs
account_ref = f"test-va-{uuid.uuid4().hex[:8]}"
account_name = "Vilapay Test Group"

va_headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}
if ACCOUNT_ID:
    va_headers["accountId"] = ACCOUNT_ID

va_response = requests.post(
    f"{NOMBA_BASE_URL}/accounts/virtual",
    json={
        "accountRef": account_ref,
        "accountName": account_name,
    },
    headers=va_headers,
)

print(f"VA creation status: {va_response.status_code}")
va_data = va_response.json()
print(f"Response: {va_data}")

# ── Step 3: List existing virtual accounts ────────────────────────────────────
print()
print("Step 3: Listing existing virtual accounts...")

list_response = requests.get(
    f"{NOMBA_BASE_URL}/accounts/virtual",
    headers=va_headers,
)

print(f"List status: {list_response.status_code}")
print(f"Response: {list_response.json()}")
