from decouple import config

from .base import *

# ── Core ──────────────────────────────────────────────────────────────────────
SECRET_KEY = config("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = ["vilapay.ng", "www.vilapay.ng", "vila.pay", "api.vilapay.ng"]

# ── Database — local PostgreSQL on Azure VM ────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": config("DB_NAME", default="vilapay"),
        "USER": config("DB_USER", default="vilapay"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
    }
}

# ── Redis — local on Azure VM ─────────────────────────────────────────────────
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "https://vilapay.ng",
    "https://www.vilapay.ng",
    "https://vila.pay",
]

# ── Nomba production credentials ──────────────────────────────────────────────
NOMBA_CLIENT_ID = config("NOMBA_CLIENT_ID")
NOMBA_CLIENT_SECRET = config("NOMBA_CLIENT_SECRET")
NOMBA_ACCOUNT_ID = config("NOMBA_ACCOUNT_ID")
NOMBA_BASE_URL = "https://api.nomba.com/v1"
NOMBA_SANDBOX = False
NOMBA_WEBHOOK_SECRET = config("NOMBA_WEBHOOK_SECRET")

# ── DRF — JSON only in production ─────────────────────────────────────────────
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

# ── Security headers ──────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_PASSWORD", default="")
DEFAULT_FROM_EMAIL = "Vilapay <noreply@vilapay.ng>"

# ── Logging (production) ──────────────────────────────────────────────────────
# console   → stdout → systemd/journald  (journalctl -u vilapay-backend)
# app_file  → /var/log/vilapay/app.log   INFO+  10 MB × 10 rotations
# error_file→ /var/log/vilapay/error.log ERROR+ 5 MB  × 20 rotations
# security  → /var/log/vilapay/security.log — auth, webhook, CSRF events

_LOG_DIR = "/var/log/vilapay"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": LOG_FORMATTERS,
    "filters": LOG_FILTERS,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{_LOG_DIR}/app.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{_LOG_DIR}/error.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 20,
            "formatter": "verbose",
            "level": "ERROR",
            "encoding": "utf-8",
        },
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
        "handlers": ["console", "app_file", "error_file"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "security_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
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
