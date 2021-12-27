from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.filters import BaseFilterBackend

from apps.utils import extract_user_from_request_token


class DjanghiModelBackend(ModelBackend):
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
            # Comment below is copied from Django
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


class CustomAuthenticationMiddleware(AuthenticationMiddleware):

    def process_request(self, request):
        super().process_request(request)

        if isinstance(request.user, AnonymousUser):
            user_from_token = extract_user_from_request_token(request)
            if user_from_token:
                request.user = user_from_token


class AssociationFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user and queryset.exists() and hasattr(queryset[0], 'association'):
            return queryset.filter(association_id=request.user.association_id)

        return queryset
