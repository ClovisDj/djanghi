from rest_framework import routers

from apps.associations.views import MembershipContributionFieldsModelViewSet, ContribFieldOptInModelViewSet

app_name = 'associations'
router = routers.SimpleRouter(trailing_slash=False)

router.register(r'contribution_fields', MembershipContributionFieldsModelViewSet, basename='contribution-fields')
router.register(r'contribution_field_opt_ins', ContribFieldOptInModelViewSet,
                basename='contrib-field_opt_ins')

urlpatterns = [
]

urlpatterns += router.urls
