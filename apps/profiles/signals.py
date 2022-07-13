import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.profiles.models import UserRegistrationLink, PasswordResetLink
from apps.utils import send_html_templated_email

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserRegistrationLink)
def send_user_registration_link(sender, instance, created, **kwargs):
    if instance.should_send_activation and instance.send_time is None:
        context = {
            'association_label': instance.association.label,
            'registration_link': instance.link,
            'host': settings.API_HOST,
        }

        is_successful = send_html_templated_email(
            [instance.user.email],
            'emails/registration.html',
            f'{instance.association.label.title()} - Djanghi registration',
            'registration',
            context=context
        )

        if is_successful:
            instance.send_time = timezone.now()
            instance.save()


@receiver(post_save, sender=PasswordResetLink)
def send_password_reset_link(sender, instance, created, **kwargs):
    if instance.is_active:
        context = {
            'first_name': instance.user.first_name,
            'association_label': instance.association.label,
            'password_reset_link': instance.link,
            'host': settings.API_HOST,
        }

        send_html_templated_email(
            [instance.user.email],
            'emails/password-reset.html',
            f'{instance.association.label.title()} - Password Reset',
            'password reset link',
            context=context
        )
