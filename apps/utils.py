import uuid

from django.contrib.auth.backends import ModelBackend
from django.db import models


class UUIDModelMixin(models.Model):
    id = models.UUIDField(db_index=True, primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CreateUpdateDateMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class DjanghiCustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        from apps.profiles.models import User

        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return

        user_kwargs = {
            'email': username
        }
        association_label = kwargs.get('association')
        if association_label:
            user_kwargs['association__label__iexact'] = association_label

        try:
            user = User.objects.get(**user_kwargs)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        from apps.profiles.models import User

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
