from django.apps import AppConfig


class TactictoeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tactictoe'

    def ready(self):
        import tactictoe.signals
