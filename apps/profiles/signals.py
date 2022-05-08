import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.profiles.models import UserRegistrationLink

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserRegistrationLink)
def send_user_registration_link(sender, instance, created, **kwargs):
    if instance.should_send_activation:
        html_message = f"<html>html Hello,\n Please click the link below to complete your account activation.\n" \
                       f"Thank you!\n {instance.link}</html>"

        msg = EmailMultiAlternatives(
            subject=f'{instance.association.label} Djanghi portal registration invite',
            from_email=f"{settings.DEFAULT_FROM_EMAIL}",
            to=[instance.user.email]
        )
        msg.attach_alternative(html_message, "text/html")

        try:
            msg.send()
        except Exception as exc:
            logger.info(f'Could not send registration email for: {instance.user.email}. Message: {str(exc)}')
