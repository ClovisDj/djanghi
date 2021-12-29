from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import BaseFilterBackend
from rest_framework_json_api.pagination import JsonApiPageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings

from apps.utils import extract_user_from_request_token


class DjanghiModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        from apps.profiles.models import User

        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return

        user_kwargs = {
            'email': username.lower()
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
        # At this point of the process any requester should be authenticated
        # and the user object properly attached to the request
        if request.user and queryset.exists() and hasattr(queryset[0], 'association'):
            return queryset.filter(association_id=request.user.association_id)

        return queryset


class CustomJWTAuthentication(JWTAuthentication):

    def get_validated_token(self, raw_token):
        """
        Override this method so that we do not return 500 to the client instead we return 403
        """
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError:
                pass

        raise PermissionDenied()


class CustomJsonApiPageNumberPagination(JsonApiPageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000
