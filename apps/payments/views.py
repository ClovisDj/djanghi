from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from apps.payments.filters import MembershipPaymentFilter
from apps.payments.models import MembershipPayment, MembershipPaymentSatus
from apps.payments.serializers import MembershipPaymentModelSerializer, MembershipPaymentSatusModelSerializer
from apps.profiles import roles


class MembershipPaymentModelViewSet(mixins.CreateModelMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.ListModelMixin,
                                    GenericViewSet):

    queryset = MembershipPayment.objects.all()
    serializer_class = MembershipPaymentModelSerializer
    filterset_class = MembershipPaymentFilter
    allowed_admin_roles = (roles.FULL_ADMIN, roles.PAYMENT_MANAGER, roles.COST_MANAGER, )
    regular_user_allowed_actions = ('get', )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.parser_context['kwargs']['user_pk'])


class MembershipPaymentStatusModelViewSet(mixins.ListModelMixin,
                                          mixins.RetrieveModelMixin,
                                          GenericViewSet):

    queryset = MembershipPaymentSatus.objects.all().order_by('membership_payment_type__name')
    serializer_class = MembershipPaymentSatusModelSerializer
    allowed_admin_roles = (roles.FULL_ADMIN, roles.PAYMENT_MANAGER, roles.COST_MANAGER, )
    regular_user_allowed_actions = ('get', )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.parser_context['kwargs']['user_pk'])
