import json

from django.conf import settings
from django.db import transaction
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from rest_framework import mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_json_api.views import AutoPrefetchMixin
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.associations.models import Association
from apps.mixins import RequestLinkValidation
from apps.permissions import IsUserOrAdmin, IsFullAdmin, PasswordResetPermission
from apps.profiles import serializers, roles
from apps.profiles.models import User, UserRegistrationLink, PasswordResetLink
from apps.profiles.serializers import UserModelSerializer, UserAdminModelSerializer, UserRegistrationModelSerializer, \
    UserRegistrationForm, PasswordResetLinkModelSerializer, PasswordResetForm
from apps.utils import is_valid_uuid, _force_login


class ApiLoginView(TokenObtainPairView):
    http_method_names = ('post', )
    serializer_class = serializers.LoginSerializer


class UserModelViewSet(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       AutoPrefetchMixin,
                       GenericViewSet):

    queryset = User.objects.get_actives().prefetch_related('roles')
    serializer_class = UserModelSerializer
    search_fields = ('first_name', 'last_name', 'email', )
    permission_classes = (permissions.IsAuthenticated, IsUserOrAdmin, )

    def get_serializer_class(self):
        # Due to rest-framework-json-api exception handling, we have to do soft check here se below:
        # https://github.com/django-json-api/django-rest-framework-json-api/blob/e9ca8d9348dc71eda0a48e5c71d83a6526ca2711/rest_framework_json_api/utils.py#L380
        is_admin = getattr(self.request.user, 'is_admin', False)
        if is_admin:
            return UserAdminModelSerializer
        return super().get_serializer_class()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['post'], permission_classes=[IsFullAdmin])
    @transaction.atomic
    def admin(self, request, pk=None):
        user_obj = self.get_object()
        user_obj.roles.clear()
        user_obj.add_roles(*request.data.get('roles', []))
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRegistrationViewSet(mixins.CreateModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.ListModelMixin,
                              AutoPrefetchMixin,
                              GenericViewSet):

    queryset = UserRegistrationLink.objects.all()
    serializer_class = UserRegistrationModelSerializer

    allowed_admin_roles = (roles.FULL_ADMIN, roles.PAYMENT_MANAGER, roles.COST_MANAGER, )


class BaseFormView(View):
    link_related_name = None

    def get_context(self):
        return {
            'association': self.association,
            'year': str(timezone.now().year)
        }

    def get(self, request, *args, **kwargs):
        if not self.request_is_valid(kwargs.get('association'), kwargs.get('user'), kwargs.get('link'),
                                     self.link_related_name):
            return HttpResponseNotFound()

        context = {**self.get_context(), 'form': self.form_class()}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if not self.request_is_valid(kwargs.get('association'), kwargs.get('user'), kwargs.get('link'),
                                     self.link_related_name):
            return HttpResponseNotFound()

        if form.is_valid():
            activated_user = form.activation_actions(self.link.user, form.cleaned_data)
            form.deactivate_link(self.link)
            login_data = _force_login(activated_user)
            redirect_url = f'{settings.FRONT_END_HOST}/activated?refresh={login_data[0]}&access={login_data[1]}'
            return HttpResponseRedirect(redirect_url)

        error_message = []
        for field, error_list in json.loads(form.errors.as_json()).items():
            for error_dict in error_list:
                error_message.append(error_dict['message'])

        context = {
            **self.get_context(),
            'form': form,
            'errors': error_message
        }
        return render(request, self.template_name, context=context)


class UserRegistrationView(RequestLinkValidation, BaseFormView):
    template_name = 'forms/registration.html'
    form_class = UserRegistrationForm
    link_related_name = 'registration_links'


class PasswordResetView(RequestLinkValidation, BaseFormView):
    template_name = 'forms/password-reset.html'
    form_class = PasswordResetForm
    link_related_name = 'password_resets'


class PasswordResetLinkModelViewSet(mixins.CreateModelMixin,
                                    GenericViewSet):

    queryset = PasswordResetLink.objects.all()
    serializer_class = PasswordResetLinkModelSerializer
    permission_classes = (PasswordResetPermission, )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
