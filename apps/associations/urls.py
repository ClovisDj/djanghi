from rest_framework import routers

from apps.associations.views import MembershipContributionFieldsModelViewSet

app_name = 'associations'
router = routers.SimpleRouter(trailing_slash=False)

router.register(r'contribution_fields', MembershipContributionFieldsModelViewSet, basename='contribution-fields')

urlpatterns = [
]

urlpatterns += router.urls
