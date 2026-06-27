import json
from datetime import timedelta
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

AUTH_USER_MODEL = "users.User"


def get_secret(secret_name, region_name="eu-west-1"):
    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        raise e


INSTALLED_APPS = [
    "django_prometheus",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    "django_celery_beat",
    # Local apps
    "apps.users",
    "apps.groups",
    "apps.wallets",
    "apps.payments",
    "apps.payouts",
    "apps.notifications",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# API Docs
SPECTACULAR_SETTINGS = {
    "TITLE": "Vilapay API",
    "DESCRIPTION": "Community rotating savings platform. Your village, your money, your turn.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Celery
CELERY_TIMEZONE = "Africa/Lagos"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Payment provider
PAYMENT_PROVIDER = "nomba"

# Public base URL of this API — used for Nomba callback URLs etc.
# Override in environment-specific settings.
VILAPAY_API_BASE_URL = "https://api.vilapay.ng"

# ── Logging ───────────────────────────────────────────────────────────────────
# Shared formatters and logger hierarchy.
# Handlers are defined per-environment (development.py / production.py).
#
# Logger hierarchy:
#   root          → catch-all for anything not named below
#   django        → Django internals (migrations, signals, etc.)
#   django.request → HTTP request errors (WARNING+ only — 404s are noise)
#   django.security → Auth failures, CSRF, host header attacks — always log
#   apps          → all code under apps/
#   services      → all code under services/
#   celery        → Celery worker and beat
#
# To temporarily enable SQL query logging in development, set the
# django.db.backends logger to DEBUG in development.py.

LOG_FORMATTERS = {
    "verbose": {
        # Full context: timestamp, level, logger name, message
        # Example: 2026-06-27 14:23:01 [INFO ] services.groups: Group activated
        "format": "{asctime} [{levelname:<7}] {name}: {message}",
        "style": "{",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    },
    "simple": {
        # For console output in development — less visual noise
        "format": "[{levelname}] {name}: {message}",
        "style": "{",
    },
}

LOG_FILTERS = {
    "require_debug_false": {
        "()": "django.utils.log.RequireDebugFalse",
    },
    "require_debug_true": {
        "()": "django.utils.log.RequireDebugTrue",
    },
}

# Celery beat schedule
CELERY_BEAT_SCHEDULE = {
    "send-contribution-reminders": {
        "task": "groups.send_contribution_reminders",
        "schedule": 86400,  # daily (seconds)
    },
    "sweep-wallets-for-contributions": {
        "task": "groups.sweep_wallets_for_contributions",
        "schedule": 86400,  # daily
    },
    "check-direct-debit-statuses": {
        "task": "payments.check_direct_debit_statuses",
        "schedule": 3600,  # hourly
    },
}
