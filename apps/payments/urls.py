from rest_framework import routers

from apps.payments.views import BulkMembershipPaymentModelViewSet, AdminMembershipPaymentStatusModelViewSet

app_name = 'payments'
router = routers.SimpleRouter(trailing_slash=False)

router.register(r'bulk_membership_payments', BulkMembershipPaymentModelViewSet, basename='bulk-payments')
router.register(r'membership_payments_status', AdminMembershipPaymentStatusModelViewSet, basename='payments-status')

urlpatterns = [
]

urlpatterns += router.urls

