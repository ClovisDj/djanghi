
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.profiles import serializers


class ApiLoginView(TokenObtainPairView):
    serializer_class = serializers.LoginSerializer
