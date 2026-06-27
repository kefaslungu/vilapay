from .base import *

# Load all secrets from AWS Secrets Manager
secrets = get_secret("vilapay/production")

SECRET_KEY = secrets["DJANGO_SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS = ["vilapay.ng", "www.vilapay.ng", "vila.pay", "api.vilapay.ng"]

# Production DB — RDS PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": secrets["DB_NAME"],
        "USER": secrets["DB_USER"],
        "PASSWORD": secrets["DB_PASSWORD"],
        "HOST": secrets["DB_HOST"],
        "PORT": secrets.get("DB_PORT", "5432"),
        "OPTIONS": {
            "sslmode": "require",
        },
    }
}

# Redis — ElastiCache
CELERY_BROKER_URL = secrets["REDIS_URL"]
CELERY_RESULT_BACKEND = secrets["REDIS_URL"]

# CORS — restrict to frontend domain only
CORS_ALLOWED_ORIGINS = [
    "https://vilapay.ng",
    "https://www.vilapay.ng",
    "https://vila.pay",
]

# Nomba production credentials
NOMBA_CLIENT_ID = secrets["NOMBA_CLIENT_ID"]
NOMBA_CLIENT_SECRET = secrets["NOMBA_CLIENT_SECRET"]
NOMBA_ACCOUNT_ID = secrets["NOMBA_ACCOUNT_ID"]
NOMBA_BASE_URL = "https://api.nomba.com/v1"
NOMBA_SANDBOX = False
NOMBA_WEBHOOK_SECRET = secrets["NOMBA_WEBHOOK_SECRET"]

# Security headers
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email — SES in production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = secrets.get("EMAIL_HOST", "email-smtp.eu-west-1.amazonaws.com")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = secrets.get("EMAIL_USER", "")
EMAIL_HOST_PASSWORD = secrets.get("EMAIL_PASSWORD", "")
DEFAULT_FROM_EMAIL = "Vilapay <noreply@vilapay.ng>"

# ── Logging (production) ──────────────────────────────────────────────────────
# Three destinations:
#   console   → stdout, captured by systemd/journald (short-term, searchable
#               with `journalctl -u vilapay-backend`)
#   app_file  → /var/log/vilapay/app.log — all INFO+ (10 MB × 10 rotations)
#   error_file→ /var/log/vilapay/error.log — ERROR+ only for quick triage
#               (5 MB × 20 rotations — errors are kept longer)
#   security  → /var/log/vilapay/security.log — auth, webhook, CSRF events
#
# The deploy script creates /var/log/vilapay/ and sets ownership to the
# vilapay user, so these paths will be writable at runtime.

_LOG_DIR = "/var/log/vilapay"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": LOG_FORMATTERS,
    "filters": LOG_FILTERS,
    "handlers": {
        # systemd/journald captures this stream
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        # Full INFO+ log — primary persistent log
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{_LOG_DIR}/app.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 10,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        # ERROR+ only — open this first when something breaks
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{_LOG_DIR}/error.log",
            "maxBytes": 5 * 1024 * 1024,   # 5 MB
            "backupCount": 20,
            "formatter": "verbose",
            "level": "ERROR",
            "encoding": "utf-8",
        },
        # Security-specific events — separate file for audit requirements
        "security_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{_LOG_DIR}/security.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 20,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "root": {
        # Catch anything not explicitly named below
        "handlers": ["console", "app_file", "error_file"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        # 4xx/5xx request errors
        "django.request": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        # Auth failures, invalid hosts, CSRF — goes to security log
        "django.security": {
            "handlers": ["console", "security_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        # Business logic — INFO in production (DEBUG is too verbose)
        "apps": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "services": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        # Webhook events need the security trail
        "services.webhooks": {
            "handlers": ["console", "app_file", "security_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.task": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
