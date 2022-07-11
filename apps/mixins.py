from django.core.exceptions import ObjectDoesNotExist


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
