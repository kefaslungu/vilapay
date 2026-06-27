#!/usr/bin/env python
"""Quick script to test Nomba API authentication."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

import requests
from decouple import Config, RepositoryEnv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
config = Config(RepositoryEnv(env_path))

NOMBA_BASE_URL = "https://sandbox.nomba.com/v1"
CLIENT_ID = config("TEST_CLIENT_ID")
CLIENT_SECRET = config("TEST_PRIVATE_KEY")
ACCOUNT_ID = config("NOMBA_ACCOUNT_ID", default="")

print(f"Client ID:  {CLIENT_ID[:6]}..." if CLIENT_ID else "Client ID: NOT SET")
print(f"Account ID: {ACCOUNT_ID[:6]}..." if ACCOUNT_ID else "Account ID: NOT SET (will try without)")
print()

print("Attempting authentication...")

headers = {"Content-Type": "application/json"}
if ACCOUNT_ID:
    headers["accountId"] = ACCOUNT_ID

response = requests.post(
    f"{NOMBA_BASE_URL}/auth/token/issue",
    json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    },
    headers=headers,
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
