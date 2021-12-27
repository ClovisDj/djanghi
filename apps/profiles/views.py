from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.profiles import serializers
from apps.profiles.models import User
from apps.profiles.serializers import UserModelSerializer


class ApiLoginView(TokenObtainPairView):
    serializer_class = serializers.LoginSerializer


class UserModelViewSet(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):

    queryset = User.objects.get_actives()
    serializer_class = UserModelSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
