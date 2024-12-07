from celery import Celery
from ..core.config import settings

app = Celery(
    'tasks',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1',
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1'
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)