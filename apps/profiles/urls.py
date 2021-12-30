from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from apps.profiles.views import ApiLoginView, UserModelViewSet, UserRegistrationViewSet

app_name = 'profiles'
router = routers.SimpleRouter(trailing_slash=False)

router.register(r'users', UserModelViewSet, basename='users')
router.register(r'registrations', UserRegistrationViewSet, basename='registrations')

urlpatterns = [
    path('obtain_token', ApiLoginView.as_view(), name='login_view'),
    path('refresh_token', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls
