from django.apps import AppConfig


class StarsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stars'

    def ready(self):
        import stars.signals