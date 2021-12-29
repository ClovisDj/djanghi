from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.permissions import IsUserOrFullAdmin
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
    permission_classes = (permissions.IsAuthenticated, IsUserOrFullAdmin, )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
