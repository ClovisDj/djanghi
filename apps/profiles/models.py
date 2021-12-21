import uuid

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

from apps.utils import CreateUpdateDateMixin, UUIDModelMixin


class UserRole(CreateUpdateDateMixin, UUIDModelMixin, models.Model):
    value = models.CharField(max_length=2, null=False, blank=False, unique=True)
    description = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return '[(%s) %s ID: %s]' % (self.value, self.__class__.__name__, self.pk)


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


class User(AbstractUser):
    # Had to paste these here due to circular import
    id = models.UUIDField(db_index=True, primary_key=True, default=uuid.uuid4, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # User meta data
    date_of_birth = models.DateField(null=True, blank=True)
    city_of_birth = models.CharField(max_length=100, null=True, blank=True)
    country_of_birth = models.CharField(max_length=100, null=True, blank=True)

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
    roles = models.ManyToManyField(UserRole, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email', 'association'], name='unique_username_by_association')
        ]

    def save(self, *args, **kwargs):
        self.username = self.email

        return super().save(*args, **kwargs)
