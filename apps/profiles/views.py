from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.permissions import IsUserOrFullAdmin, IsAdmin
from apps.profiles import serializers
from apps.profiles.models import User, UserRegistrationLink
from apps.profiles.serializers import UserModelSerializer, UserAdminModelSerializer, UserRegistrationModelSerializer


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

    def get_serializer_class(self):
        if self.request.user.is_admin:
            return UserAdminModelSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class UserRegistrationViewSet(mixins.CreateModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):

    queryset = UserRegistrationLink.objects.all()
    serializer_class = UserRegistrationModelSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdmin, )
