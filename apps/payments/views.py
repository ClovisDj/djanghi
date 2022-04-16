from django.db import transaction
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.payments.filters import MembershipPaymentFilter
from apps.payments.models import MembershipPayment, MembershipPaymentSatus
from apps.payments.serializers import MembershipPaymentModelSerializer, MembershipPaymentSatusModelSerializer, \
    BulkMembershipPaymentModelSerializer
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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

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


class BulkMembershipPaymentModelViewSet(mixins.CreateModelMixin,
                                        GenericViewSet):

    queryset = MembershipPayment.objects.all()
    serializer_class = BulkMembershipPaymentModelSerializer
    allowed_admin_roles = (roles.FULL_ADMIN, roles.PAYMENT_MANAGER, roles.COST_MANAGER, )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED, headers=headers)
