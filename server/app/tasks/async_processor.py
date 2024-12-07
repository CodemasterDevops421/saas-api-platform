from celery import Celery
from celery.signals import task_prerun, task_postrun
from prometheus_client import Counter, Histogram
from typing import Dict, Any
from ..core.config import settings

celery_app = Celery('tasks', broker=settings.REDIS_URL)

task_duration = Histogram('task_duration_seconds', 'Task execution time')
task_count = Counter('tasks_total', 'Number of tasks processed', ['status'])

@celery_app.task(bind=True, max_retries=3)
def process_analytics_data(self, data: Dict[str, Any]):
    try:
        # Process large analytics datasets
        with task_duration.time():
            result = analyze_data(data)
        task_count.labels(status='success').inc()
        return result
    except Exception as exc:
        task_count.labels(status='failed').inc()
        raise self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=3)
def sync_subscription_data(self, user_id: int):
    try:
        # Sync subscription status with Stripe
        with task_duration.time():
            result = sync_stripe_data(user_id)
        task_count.labels(status='success').inc()
        return result
    except Exception as exc:
        task_count.labels(status='failed').inc()
        raise self.retry(exc=exc)

@celery_app.task
def cleanup_old_data():
    try:
        with task_duration.time():
            cleanup_database()
            cleanup_cache()
        task_count.labels(status='success').inc()
    except Exception:
        task_count.labels(status='failed').inc()
        raise

celery_app.conf.beat_schedule = {
    'cleanup-old-data': {
        'task': 'tasks.cleanup_old_data',
        'schedule': 3600.0  # hourly
    }
}