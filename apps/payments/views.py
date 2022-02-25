from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet

from apps.payments.models import MembershipPayment
from apps.payments.serializers import MembershipPaymentModelSerializer
from apps.permissions import AdminAccessPolicyPermission, RegularUserActionPermissions
from apps.profiles import roles


class MembershipPaymentModelViewSet(mixins.CreateModelMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.ListModelMixin,
                                    GenericViewSet):

    queryset = MembershipPayment.objects.all()
    serializer_class = MembershipPaymentModelSerializer
    permission_classes = (permissions.IsAuthenticated, AdminAccessPolicyPermission, RegularUserActionPermissions, )
    allowed_admin_roles = (roles.FULL_ADMIN, roles.PAYMENT_MANAGER, roles.COST_MANAGER, )
    regular_user_allowed_actions = ('GET', )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.parser_context['kwargs']['user_pk'])
