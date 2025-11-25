from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'
    
    def ready(self):
        # Import tasks when the app is ready to avoid import issues
        try:
            from . import stock_tasks  # noqa
        except ImportError:
            pass