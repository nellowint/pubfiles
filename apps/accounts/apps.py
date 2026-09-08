from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'apps.accounts'
    verbose_name='Usuários'

    def ready(self):
        from . import signals
