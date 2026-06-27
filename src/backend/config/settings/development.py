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
NOMBA_CLIENT_ID = config("NOMBA_CLIENT_ID", default="")
NOMBA_CLIENT_SECRET = config("NOMBA_CLIENT_SECRET", default="")
NOMBA_ACCOUNT_ID = config("NOMBA_ACCOUNT_ID", default="")
NOMBA_BASE_URL = "https://api.nomba.com/v1"
NOMBA_SANDBOX = True

# Email — console backend in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
