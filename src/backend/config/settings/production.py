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
