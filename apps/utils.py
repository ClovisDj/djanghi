import uuid

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import get_template
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken


class UUIDModelMixin(models.Model):
    id = models.UUIDField(db_index=True, primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CreateUpdateDateMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


def is_valid_uuid(uuid_str, version=4):
    if not isinstance(uuid_str, (str, uuid.UUID)):
        return False

    try:
        uuid_obj = uuid.UUID(uuid_str, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_str


def extract_user_from_request_token(request):
    from apps.custom_authentications import CustomJWTAuthentication

    try:
        is_authenticated = CustomJWTAuthentication().authenticate(request)
    except AuthenticationFailed:
        return None

    if is_authenticated:
        return is_authenticated[0]

    return None


def _force_login(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)


def send_html_templated_email(recipients, template_path, subject, email_type, context=None):
    import logging
    logger = logging.getLogger(__name__)

    assert isinstance(recipients, list)
    assert len(recipients) > 0

    logger.info(f'Start sending email {email_type} for: {recipients}')
    context = context if isinstance(context, dict) else {}

    html_template = get_template(template_path)
    html_message = html_template.render(context=context)

    msg = EmailMultiAlternatives(
        subject=subject,
        to=recipients
    )
    msg.attach_alternative(html_message, "text/html")

    try:
        msg.send()
    except Exception as exc:
        logger.info(f'Could not send {email_type} email for: {recipients}. Message: {str(exc)}')
        return False

    logger.info(f'Successfully sent {email_type} email for: {recipients}')
    return True
