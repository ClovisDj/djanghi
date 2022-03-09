import uuid

from django.db import models
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
    try:
        uuid_obj = uuid.UUID(uuid_str, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_str


def extract_user_from_request_token(request):
    from apps.extensions.backend import CustomJWTAuthentication

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
