from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all apps
app.autodiscover_tasks()

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')


from celery.schedules import crontab

# Explicitly import task modules to ensure they're registered
app.conf.update(
    imports=['shop.stock_tasks']
)

app.conf.beat_schedule = {
    'auto-cancel-orders-every-minute': {
        'task': 'shop.stock_tasks.auto_cancel_unpaid_orders',
        'schedule': crontab(minute='*/1'),  # Run every 1 minute
    },
}
