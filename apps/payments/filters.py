from django_filters import rest_framework as filters

from apps.payments.models import MembershipPayment


class MembershipPaymentFilter(filters.FilterSet):
    contribution_id = filters.UUIDFilter(field_name="membership_payment_type_id")

    class Meta:
        model = MembershipPayment
        fields = ('contribution_id', )
