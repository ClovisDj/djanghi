from django.contrib.auth.backends import ModelBackend
from rest_framework.filters import BaseFilterBackend
from rest_framework_json_api.pagination import JsonApiPageNumberPagination


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
        association_label = kwargs.get('association_label')
        if association_label:
            user_kwargs['association__label__iexact'] = association_label

        try:
            user = User.objects.get_actives().filter(is_registered=True).get(**user_kwargs)
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


class AssociationFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        # At this point of the process any requester should be authenticated
        # and the user object properly attached to the request
        if request.user and queryset.exists() and hasattr(queryset.model, 'association'):
            return queryset.filter(association_id=request.user.association_id)

        return queryset


class CustomJsonApiPageNumberPagination(JsonApiPageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000
