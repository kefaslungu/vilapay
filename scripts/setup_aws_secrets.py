#!/usr/bin/env python
"""
Create or update the vilapay/production secret in AWS Secrets Manager.

Run this once before deploying to production:
    python scripts/setup_aws_secrets.py

Prerequisites:
    - AWS CLI configured (aws configure) or AWS_* env vars set
    - boto3 installed (pip install boto3)
    - Fill in all values below before running (or pass via env vars)
"""
import json
import os
import sys

import boto3
from botocore.exceptions import ClientError

SECRET_NAME = "vilapay/production"
REGION = os.environ.get("AWS_REGION", "eu-west-1")

# ── Secret payload ────────────────────────────────────────────────────────────
# Fill these in OR set matching environment variables before running.
# NEVER commit this file with real values filled in.
secret_value = {
    "DJANGO_SECRET_KEY": os.environ.get("PROD_SECRET_KEY", "FILL_ME_IN"),
    # Database (RDS PostgreSQL)
    "DB_NAME": os.environ.get("PROD_DB_NAME", "vilapay"),
    "DB_USER": os.environ.get("PROD_DB_USER", "vilapay"),
    "DB_PASSWORD": os.environ.get("PROD_DB_PASSWORD", "FILL_ME_IN"),
    "DB_HOST": os.environ.get("PROD_DB_HOST", "FILL_ME_IN.rds.amazonaws.com"),
    "DB_PORT": "5432",
    # Redis (ElastiCache)
    "REDIS_URL": os.environ.get("PROD_REDIS_URL", "redis://FILL_ME_IN:6379/0"),
    # Nomba production credentials (from Nomba dashboard → Live mode)
    "NOMBA_CLIENT_ID": os.environ.get("NOMBA_CLIENT_ID", "FILL_ME_IN"),
    "NOMBA_CLIENT_SECRET": os.environ.get("NOMBA_CLIENT_SECRET", "FILL_ME_IN"),
    "NOMBA_ACCOUNT_ID": os.environ.get("NOMBA_ACCOUNT_ID", "FILL_ME_IN"),
    "NOMBA_WEBHOOK_SECRET": os.environ.get("NOMBA_WEBHOOK_SECRET", "FILL_ME_IN"),
    # Email (SES)
    "EMAIL_HOST": "email-smtp.eu-west-1.amazonaws.com",
    "EMAIL_USER": os.environ.get("SES_SMTP_USER", ""),
    "EMAIL_PASSWORD": os.environ.get("SES_SMTP_PASSWORD", ""),
}

unfilled = [k for k, v in secret_value.items() if v == "FILL_ME_IN"]
if unfilled:
    print("ERROR: The following values are not set:")
    for k in unfilled:
        print(f"  - {k}")
    print("\nSet them as environment variables and re-run, e.g.:")
    print("  PROD_SECRET_KEY=... PROD_DB_PASSWORD=... python scripts/setup_aws_secrets.py")
    sys.exit(1)

client = boto3.client("secretsmanager", region_name=REGION)

try:
    client.describe_secret(SecretId=SECRET_NAME)
    # Secret exists — update it
    client.put_secret_value(
        SecretId=SECRET_NAME,
        SecretString=json.dumps(secret_value),
    )
    print(f"Updated secret '{SECRET_NAME}' in {REGION}.")
except client.exceptions.ResourceNotFoundException:
    # Secret doesn't exist — create it
    client.create_secret(
        Name=SECRET_NAME,
        Description="Vilapay production credentials",
        SecretString=json.dumps(secret_value),
        Tags=[
            {"Key": "Project", "Value": "vilapay"},
            {"Key": "Environment", "Value": "production"},
        ],
    )
    print(f"Created secret '{SECRET_NAME}' in {REGION}.")
except ClientError as e:
    print(f"AWS error: {e}")
    sys.exit(1)

print("\nDone. The EC2/ECS instance role must have:")
print(f"  secretsmanager:GetSecretValue on arn:aws:secretsmanager:{REGION}:*:secret:{SECRET_NAME}*")
