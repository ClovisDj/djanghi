from django_filters import rest_framework as filters

from apps.payments.models import MembershipPayment, MembershipPaymentSatus
from apps.utils import is_valid_uuid


class MembershipPaymentFilter(filters.FilterSet):
    contribution_id = filters.UUIDFilter(field_name="membership_payment_type_id")

    class Meta:
        model = MembershipPayment
        fields = ('contribution_id', )


class MembershipPaymentsStatusFilter(filters.FilterSet):
    contribution_id = filters.UUIDFilter(field_name="membership_payment_type_id")
    user_ids = filters.CharFilter(method='filter_by_ids')

    class Meta:
        model = MembershipPaymentSatus
        fields = ('membership_payment_type_id', "user_id")

    # @staticmethod
    def filter_by_ids(self, queryset, value, *args, **kwargs):
        print(f'>>>>>>>>>>>>>> Request params: {self.request.query_params}')
        if args and len(args) > 0 and isinstance(args[0], str):
            ids = args[0].split(',')
            ids = [user_id for user_id in ids if is_valid_uuid(user_id)]
            if len(ids) > 0:
                return queryset.filter(user_id__in=ids)
        return queryset
