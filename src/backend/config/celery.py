import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "backend")
)

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("vilapay")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
