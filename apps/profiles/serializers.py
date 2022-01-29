import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework_json_api import serializers
from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserRegistrationLink


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


class UserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        read_only_fields = (
            'created_at',
            'updated_at',
            'date_joined',
            'last_login',
            'is_registered',
            'email',
            'is_active',
        )
        exclude = (
            'password',
            'username',
            'groups',
            'user_permissions',
            'is_superuser',
            'is_staff',
            'roles',
        )


class UserAdminModelSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    is_full_admin = serializers.SerializerMethodField()
    is_payment_manager = serializers.SerializerMethodField()
    is_cost_manager = serializers.SerializerMethodField()
    is_cotisation_manager = serializers.SerializerMethodField()

    class Meta:
        model = User
        read_only_fields = (
            'created_at',
            'updated_at',
            'date_joined',
            'last_login',
            'is_registered',
            'email',
            'is_active',
        )
        exclude = (
            'password',
            'username',
            'groups',
            'user_permissions',
            'is_superuser',
            'is_staff',
        )

    @staticmethod
    def get_is_admin(user):
        return user.is_admin

    @staticmethod
    def get_is_full_admin(user):
        return user.is_full_admin

    @staticmethod
    def get_is_payment_manager(user):
        return user.is_payment_manager

    @staticmethod
    def get_is_cost_manager(user):
        return user.is_cost_manager

    @staticmethod
    def get_is_cotisation_manager(user):
        return user.is_cost_manager


class UserRegistrationModelSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)

    is_active = serializers.BooleanField(read_only=True)

    included_serializers = {
        'user': UserAdminModelSerializer,
        'author': UserAdminModelSerializer,
    }

    class JSONAPIMeta:
        included_resources = ('user', 'author')

    class Meta:
        model = UserRegistrationLink
        read_only_fields = (
            'created_at',
            'updated_at',
            'user',
            'author',
            'association',
            'send_time',
            'expiration_date',
            'link',
        )
        exclude = (
            'is_deactivated',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = getattr(self, 'context', {}).get('request')
        self.__user = None

    def validate_email(self, email):
        try:
            user = User.objects.for_association(self.request.user.association).get(email=email)
        except User.DoesNotExist:
            return email

        self.__user = user
        if user.is_registered:
            raise serializers.ValidationError('This user is already registered')

        user.registration_links.all().delete()
        return email

    def get_or_create_user(self, validated_data):
        email = validated_data.pop('email')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        if self.__user:
            return self.__user, validated_data

        user_create_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'association': self.request.user.association,
            'is_active': True,
            'is_registered': False,
            'password': 'password'
        }
        return User.objects.create_user(email, **user_create_data), validated_data

    def generate_expiration_date(self):
        return timezone.now() + datetime.timedelta(
            days=self.request.user.association.registration_link_life
        )

    def create(self, validated_data):
        user, validated_data = self.get_or_create_user(validated_data)

        validated_data['expiration_date'] = self.generate_expiration_date()
        validated_data['user'] = user
        validated_data['author'] = self.request.user
        validated_data['association'] = self.request.user.association

        return UserRegistrationLink.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.expiration_date = self.generate_expiration_date()
        instance.save()

        return instance


class UserRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "First Name",
        'id': "first_name"
    }))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Last Name",
        'id': "last_name"
    }))
    password = forms.CharField(required=True, min_length=6, widget=forms.TextInput(attrs={
        'type': 'password',
        'class': 'form-control',
        'placeholder': "Your Password",
        'name': "password",
        'id': "password"
    }))
    password_verification = forms.CharField(required=True, min_length=6, widget=forms.TextInput(attrs={
        'type': 'password',
        'class': 'form-control',
        'placeholder': " Re-enter Your Password",
        'name': "password Verification",
        'id': "password_verification"
    }))

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('password') != cleaned_data.get('password_verification'):
            self.add_error('password_verification', 'Password mis-match')

        return cleaned_data

    @staticmethod
    def activate_user(user, cleaned_data):
        user.first_name = cleaned_data['first_name']
        user.last_name = cleaned_data['last_name']
        user.is_active = True
        user.is_registered = True
        user.set_password(cleaned_data['password'])
        user.save()
        return user

    @staticmethod
    def deactivate_link(link):
        link.is_deactivated = True
        link.save()
        return link
