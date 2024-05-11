from django.apps import AppConfig


class TictactoefrontendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tictactoefrontend'

    def ready(self):
        import tictactoefrontend.signals
