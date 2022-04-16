from rest_framework import routers

from apps.payments.views import BulkMembershipPaymentModelViewSet

app_name = 'payments'
router = routers.SimpleRouter(trailing_slash=False)

router.register(r'bulk_membership_payments', BulkMembershipPaymentModelViewSet, basename='bulk-payments')

urlpatterns = [
]

urlpatterns += router.urls

