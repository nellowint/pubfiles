from django.apps import AppConfig


class PublicationsConfig(AppConfig):
    name = 'apps.publications'
    verbose_name = 'Publicações'

    def ready(self):
        from . import signals
