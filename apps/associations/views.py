from rest_framework import mixins, serializers
from rest_framework.viewsets import GenericViewSet

from apps.associations.models import MemberContributionField
from apps.associations.serializers import MemberContributionFieldModelSerializer
from apps.profiles import roles


class MembershipContributionFieldsModelViewSet(mixins.CreateModelMixin,
                                               mixins.UpdateModelMixin,
                                               mixins.ListModelMixin,
                                               mixins.RetrieveModelMixin,
                                               mixins.DestroyModelMixin,
                                               GenericViewSet):

    queryset = MemberContributionField.objects.all()
    serializer_class = MemberContributionFieldModelSerializer
    allowed_admin_roles = (roles.FULL_ADMIN, )
    regular_user_allowed_actions = ('get', )

    def perform_destroy(self, instance):
        if instance.membership_payments.exists():
            raise serializers.ValidationError('This contribution field is already in use and cannot be deleted')
        instance.delete()
