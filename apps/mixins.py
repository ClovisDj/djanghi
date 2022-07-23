from django.core.exceptions import ObjectDoesNotExist

from apps.utils import is_valid_uuid


class RequestLinkValidation:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.link = None
        self.association = None
        assert self.link_related_name is not None

    def request_is_valid(self, association_id, user_id, link_id, link_related_name):
        from apps.associations.models import Association
        from apps.profiles.models import User
        from apps.utils import is_valid_uuid

        if not is_valid_uuid(association_id) or not is_valid_uuid(user_id) or not is_valid_uuid(link_id):
            return False

        try:
            self.association = Association.objects.get(id=association_id)
        except Association.DoesNotExist:
            return False

        try:
            user = User.objects.for_association(self.association).get(id=user_id)
        except User.DoesNotExist:
            return False

        try:
            link = getattr(user, link_related_name).all().get(id=link_id)
        except ObjectDoesNotExist:
            return False

        if not link.is_active:
            return False

        self.link = link

        return True


class SerializerRequestInitMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = getattr(self, 'context', {}).get('request')

    def extract_user_id_from_nested_route(self):
        return self.request.parser_context['kwargs']['user_pk']


class NesterUserViewQuerySetMixin:
    def get_queryset(self):
        queryset = super().get_queryset()

        user_pk = self.request.parser_context.get('kwargs', {}).get('user_pk')
        if is_valid_uuid(user_pk):
            return queryset.filter(user_id=user_pk)

        return queryset
