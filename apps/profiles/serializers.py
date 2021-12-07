from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(TokenObtainSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None
        self.fields['association'] = serializers.CharField(max_length=30)

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        association_label = attrs.get('association')

        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
            'association': association_label
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        refresh = self.get_token(self.user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'association': self.user.association_id
        }

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
