import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission, UserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from apps.profiles.roles import FULL_ADMIN, PAYMENT_MANAGER, COST_MANAGER, COTISATION_MANAGER
from apps.utils import CreateUpdateDateMixin, UUIDModelMixin, is_valid_uuid


class RoleManager(models.Manager):
    def get_actives(self):
        return self.all()


class UserRole(CreateUpdateDateMixin, UUIDModelMixin, models.Model):
    value = models.CharField(max_length=2, null=False, blank=False, unique=True)
    description = models.CharField(max_length=200, null=False, blank=False)

    objects = RoleManager()

    def __str__(self):
        return '[(%s) %s ID: %s]' % (self.value, self.__class__.__name__, self.description)


class CustomGroup(Group):
    # Had to paste these here due to circular import
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    association = models.ForeignKey(
        'associations.Association',
        on_delete=models.CASCADE,
        related_name='groups'
    )


class CustomPermission(Permission):
    # Had to paste these here due to circular import
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    association = models.ForeignKey(
        'associations.Association',
        on_delete=models.CASCADE,
        related_name='permissions'
    )


class CustomUserManager(UserManager):
    def get_actives(self):
        return self.filter(
            is_active=True,
            association__is_active=True,
            association_id__isnull=False,
        )

    def for_association(self, association):
        return self.filter(association=association)

    def admins(self):
        return self.annotate(num_roles=Count('roles')).filter(num_roles__gt=0)


class User(AbstractUser):
    MALE = 'M'
    FEMALE = 'F'
    UNSPECIFIED = 'U'
    SEX_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (FEMALE, 'Female'),
        (UNSPECIFIED, 'Unspecified'),
    )
    # Had to paste these here due to circular import
    id = models.UUIDField(db_index=True, primary_key=True, default=uuid.uuid4, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_registered = models.BooleanField(default=False)

    # User meta data
    date_of_birth = models.DateField(null=True, blank=True)
    city_of_birth = models.CharField(max_length=100, null=True, blank=True)
    country_of_birth = models.CharField(max_length=100, null=True, blank=True)
    sex = models.CharField(max_length=2, choices=SEX_CHOICES, default=UNSPECIFIED)
    address = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=300, null=True, blank=True)
    country = models.CharField(max_length=300, null=True, blank=True)
    state = models.CharField(max_length=300, null=True, blank=True)
    zip_code = models.CharField(max_length=300, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    # Settings
    notify_on_payment = models.BooleanField(default=True)
    receive_association_notification = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        CustomGroup,
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_pool"
    )

    user_permissions = models.ManyToManyField(
        CustomPermission,
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_pool"
    )

    association = models.ForeignKey(
        'associations.Association',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    roles = models.ManyToManyField(UserRole)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['first_name', 'email']
        constraints = [
            models.UniqueConstraint(fields=['email', 'association'], name='unique_username_by_association')
        ]

    def validate_sex_choice(self):
        sex_choice_is_valid = False
        for sex_option, _ in self.SEX_CHOICES:
            if self.sex == sex_option:
                sex_choice_is_valid = True
                break

        if not sex_choice_is_valid:
            raise ValidationError(
                {'sex': f'{self.sex} is not a valid choice'}
            )

    @property
    def can_receive_payment_notification(self):
        return (
            self.is_active and
            self.is_registered and
            self.notify_on_payment and
            self.association.is_active and
            self.association.notify_user_payments
        )

    def clean(self):
        super().clean()

        self.validate_sex_choice()

    def save(self, *args, **kwargs):
        self.username = self.email

        self.clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def get_roles(*roles):
        role_obj_list = set()
        for role in roles:
            if isinstance(role, UserRole):
                role_obj_list.add(role)
                continue

            is_uuid_str = isinstance(role, str) and is_valid_uuid(role)
            is_role_value = isinstance(role, str) and len(role) < 2
            if is_uuid_str or is_role_value:
                query_kwarg = dict(id=role) if is_uuid_str else dict(value=role.upper())
                try:
                    role_obj = UserRole.objects.get_actives().get(**query_kwarg)
                except UserRole.DoesNotExist:
                    continue
                else:
                    role_obj_list.add(role_obj)

        return role_obj_list

    def add_roles(self, *role):
        roles = self.get_roles(*role)
        if roles:
            self.roles.add(*roles)

    def user_roles_set_by(self, field_name):
        return set(self.roles.all().values_list(field_name, flat=True))

    def revoke_roles(self, *role):
        user_roles_set = self.user_roles_set_by('id')
        roles_to_revoke = self.get_roles(*role)
        roles_to_revoke_set = {role.id for role in roles_to_revoke} if roles_to_revoke else set()
        diff_roles_set = user_roles_set - roles_to_revoke_set

        if diff_roles_set:
            self.roles.clear()
            self.roles.add(*diff_roles_set)

    def has_roles(self, *roles):
        roles_obj = self.get_roles(*roles)
        if not roles_obj:
            return False

        roles_set_by_value = {role.value for role in roles_obj}
        user_roles_set = self.user_roles_set_by('value')
        return bool(roles_set_by_value.issubset(user_roles_set))

    def has_min_one_role(self, *roles):
        roles_object_set = self.get_roles(*roles)
        user_roles_set = set(self.roles.all())
        return bool(roles_object_set.intersection(user_roles_set))

    @property
    def is_full_admin(self):
        return self.has_roles(FULL_ADMIN)

    @property
    def is_payment_manager(self):
        return self.has_roles(PAYMENT_MANAGER)

    @property
    def is_cost_manager(self):
        return self.has_roles(COST_MANAGER)

    @property
    def is_cotisation_manager(self):
        return self.has_roles(COTISATION_MANAGER)

    @property
    def is_admin(self):
        return self.roles.exists()


class UserRegistrationLink(CreateUpdateDateMixin, UUIDModelMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='registration_links'
    )
    # Even though user has an association attached to, we still it here for backend filter
    association = models.ForeignKey(
        'associations.Association',
        on_delete=models.CASCADE,
        related_name='registration_links'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_registration_links'
    )
    expiration_date = models.DateTimeField(null=False, blank=False)
    send_time = models.DateTimeField(null=True, blank=True)
    is_deactivated = models.BooleanField(default=False)
    should_send_activation = models.BooleanField(default=False)
    link = models.URLField(null=False, blank=False)

    class Meta:
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        schema = 'http://' if settings.ENVIRONMENT.lower() == 'local' else 'https://'
        self.link = f'{schema}{settings.API_HOST}/activate/{str(self.association_id)}/{str(self.user_id)}/{str(self.id)}'

        return super().save(*args, **kwargs)

    @property
    def is_active(self):
        return not self.is_deactivated and timezone.now() < self.expiration_date


class PasswordResetLink(CreateUpdateDateMixin,
                        UUIDModelMixin,
                        models.Model):
    association = models.ForeignKey(
        'associations.Association',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_resets'
    )
    expiration_date = models.DateTimeField(null=False, blank=False)
    is_deactivated = models.BooleanField(default=False)
    link = models.URLField(null=False, blank=False)

    def save(self, *args, **kwargs):
        schema = 'http://' if settings.ENVIRONMENT.lower() == 'local' else 'https://'
        self.link = f'{schema}{settings.API_HOST}/password-reset/{str(self.association_id)}/{str(self.user_id)}/' \
                    f'{str(self.id)}'
        self.expiration_date = timezone.now() + settings.PASSWORD_RESET_EXPIRATION_DELTA

        return super().save(*args, **kwargs)

    @property
    def is_active(self):
        return not self.is_deactivated and timezone.now() < self.expiration_date
