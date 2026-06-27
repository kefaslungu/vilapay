from decouple import config

from .base import *

SECRET_KEY = config(
    "SECRET_KEY", default="django-insecure-dev-key-change-in-production"
)

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Local DB for development
DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": config("DB_NAME", default="vilapay_dev"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Local Redis for development
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")

# CORS — allow all in dev
CORS_ALLOW_ALL_ORIGINS = True

# Nomba sandbox credentials — loaded from .env in development
NOMBA_CLIENT_ID = config("TEST_CLIENT_ID", default="")
NOMBA_CLIENT_SECRET = config("TEST_PRIVATE_KEY", default="")
NOMBA_ACCOUNT_ID = config("NOMBA_ACCOUNT_ID", default="")
NOMBA_BASE_URL = "https://sandbox.nomba.com/v1"
NOMBA_SANDBOX = True

# Use ngrok (or similar) URL here when testing Nomba sandbox callbacks locally
VILAPAY_API_BASE_URL = "http://localhost:8000"

# Email — console backend in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── Logging (development) ─────────────────────────────────────────────────────
# Everything at DEBUG to the console.
# To see SQL queries too, change django.db.backends to DEBUG.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": LOG_FORMATTERS,
    "filters": LOG_FILTERS,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        # Django internals — INFO so migration output stays visible
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        # Request errors only (skip 404s and redirects)
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        # Always log security events
        "django.security": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        # SQL query logging — uncomment when debugging DB issues
        # "django.db.backends": {
        #     "handlers": ["console"],
        #     "level": "DEBUG",
        #     "propagate": False,
        # },
        # App code — full DEBUG
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "services": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
