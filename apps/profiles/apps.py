import logging
from django.apps import AppConfig
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles'

    @staticmethod
    def create_role_objects(sender, **kwargs):
        from .roles import ROLE_DEFINITIONS
        from .models import UserRole

        for role_kwargs in ROLE_DEFINITIONS:
            created, bool_value = UserRole.objects.get_or_create(**role_kwargs)
            logger.info(f'{created}, object created: {bool_value}')

    def ready(self):
        import apps.profiles.signals    # Import needed for signal to work
        post_migrate.connect(self.create_role_objects, sender=self)
