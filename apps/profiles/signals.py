import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils import timezone

from apps.profiles.models import UserRegistrationLink

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserRegistrationLink)
def send_user_registration_link(sender, instance, created, **kwargs):
    if instance.should_send_activation and instance.send_time is None:
        logger.info(f'Start sending registration email for: {instance.user.email}')
        context = {
            'association_label': instance.association.label,
            'registration_link': instance.link,
            'host': settings.API_HOST,
        }
        registration_template = get_template('emails/registration.html')
        html_message = registration_template.render(context=context)

        msg = EmailMultiAlternatives(
            subject=f'{instance.association.label} - Djanghi registration',
            to=[instance.user.email]
        )
        msg.attach_alternative(html_message, "text/html")

        try:
            msg.send()
        except Exception as exc:
            logger.info(f'Could not send registration email for: {instance.user.email}. Message: {str(exc)}')
        else:
            instance.send_time = timezone.now()
            instance.save()
            logger.info(f'Successfully sent registration email for: {instance.user.email}')
