import time

from celery import Celery

from src.emgmt.config import settings

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND


@celery.task(name="create task")
def create_task(a, b, c):
    time.sleep(a)
    return b + c
