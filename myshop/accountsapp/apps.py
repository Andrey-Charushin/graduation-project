from django.apps import AppConfig


class AccountsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accountsapp'

    def ready(self):
        import accountsapp.signals
