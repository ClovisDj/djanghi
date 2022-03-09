from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from apps.payments.models import MembershipPayment, MembershipPaymentSatus
from apps.payments.serializers import MembershipPaymentModelSerializer, MembershipPaymentSatusModelSerializer
from apps.profiles import roles


class MembershipPaymentModelViewSet(mixins.CreateModelMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.ListModelMixin,
                                    GenericViewSet):

    queryset = MembershipPayment.objects.all()
    serializer_class = MembershipPaymentModelSerializer
    allowed_admin_roles = (roles.FULL_ADMIN, roles.PAYMENT_MANAGER, roles.COST_MANAGER, )
    regular_user_allowed_actions = ('get', )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.parser_context['kwargs']['user_pk'])


class MembershipPaymentStatusModelViewSet(mixins.ListModelMixin,
                                          mixins.RetrieveModelMixin,
                                          GenericViewSet):

    queryset = MembershipPaymentSatus.objects.all()
    serializer_class = MembershipPaymentSatusModelSerializer
    allowed_admin_roles = (roles.FULL_ADMIN, roles.PAYMENT_MANAGER, roles.COST_MANAGER, )
    regular_user_allowed_actions = ('get', )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.parser_context['kwargs']['user_pk'])
