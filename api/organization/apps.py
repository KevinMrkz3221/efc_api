from django.apps import AppConfig
from django.db.models.signals import post_migrate


class OrganizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.organization'

    def ready(self):
        import api.organization.signals  # noqa