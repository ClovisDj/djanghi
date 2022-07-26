from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from apps.profiles.views import ApiLoginView, UserRegistrationViewSet, UserRegistrationView, \
    PasswordResetLinkModelViewSet, PasswordResetView, ContribFieldOptInModelViewSet

app_name = 'profiles'
router = routers.SimpleRouter(trailing_slash=False)

router.register(r'registrations', UserRegistrationViewSet, basename='registrations')
router.register(r'reset-password', PasswordResetLinkModelViewSet, basename='reset-password')
router.register(r'contribution_field_opt_ins', ContribFieldOptInModelViewSet,
                basename='contrib-field-opt-ins')

urlpatterns = [
    path('obtain_token', ApiLoginView.as_view(), name='login_view'),
    path('refresh_token', TokenRefreshView.as_view(), name='token_refresh'),
    path(
        'activate/<str:association>/<str:user>/<str:link>',
        UserRegistrationView.as_view(),
        name='user-registration'
    ),
    path(
        'password-reset/<str:association>/<str:user>/<str:link>',
        PasswordResetView.as_view(),
        name='password-reset'
    ),
]

urlpatterns += router.urls
