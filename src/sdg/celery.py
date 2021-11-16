from celery import Celery

from sdg.setup import setup_env

setup_env()

app = Celery("sdg")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
