from django.db import transaction
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
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

    queryset = MemberContributionField.objects.active().all()
    serializer_class = MemberContributionFieldModelSerializer
    allowed_admin_roles = (roles.FULL_ADMIN, )
    regular_user_allowed_actions = ('get', )

    def perform_destroy(self, instance):
        if instance.membership_payments.exists():
            raise serializers.ValidationError('This contribution field is already in use and cannot be deleted')
        instance.delete()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def archive(self, request, pk=None):
        contrib_field = self.get_object()

        if not contrib_field.archived:
            contrib_field.archived = True
            contrib_field.archived_by = request.user
            contrib_field.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
