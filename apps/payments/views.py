from django.db import transaction
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_json_api.views import AutoPrefetchMixin

from apps.mixins import NesterUserViewQuerySetMixin
from apps.payments.filters import MembershipPaymentFilter, MembershipPaymentsStatusFilter
from apps.payments.models import MembershipPayment, MembershipPaymentSatus
from apps.payments.serializers import MembershipPaymentModelSerializer, MembershipPaymentSatusModelSerializer, \
    BulkMembershipPaymentModelSerializer
from apps.profiles import roles


SEARCH_FIELDS = (
    'user__username',
    'user__first_name',
    'user__last_name',
    'user__email',
)


class MembershipPaymentModelViewSet(mixins.CreateModelMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.ListModelMixin,
                                    AutoPrefetchMixin,
                                    NesterUserViewQuerySetMixin,
                                    GenericViewSet):

    queryset = MembershipPayment.objects.all()
    serializer_class = MembershipPaymentModelSerializer
    filterset_class = MembershipPaymentFilter
    allowed_admin_roles = (roles.FULL_ADMIN, roles.PAYMENT_MANAGER, roles.COST_MANAGER, )
    regular_user_allowed_actions = ('get', )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class AdminMembershipPaymentStatusModelViewSet(mixins.ListModelMixin,
                                               mixins.RetrieveModelMixin,
                                               NesterUserViewQuerySetMixin,
                                               AutoPrefetchMixin,
                                               GenericViewSet):

    queryset = MembershipPaymentSatus.objects.all().order_by('membership_payment_type__name')
    serializer_class = MembershipPaymentSatusModelSerializer
    filterset_class = MembershipPaymentsStatusFilter
    search_fields = SEARCH_FIELDS
    allowed_admin_roles = (roles.FULL_ADMIN, roles.PAYMENT_MANAGER, roles.COST_MANAGER, )


class MembershipPaymentStatusModelViewSet(AdminMembershipPaymentStatusModelViewSet):
    regular_user_allowed_actions = ('get', )


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
