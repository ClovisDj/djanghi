import datetime

import pytest
from django.utils import timezone

from apps.profiles.models import UserRegistrationLink, PasswordResetLink


@pytest.fixture(autouse=True)
def email_backend_setup(settings):
    settings.EMAIL_BACKEND = 'anymail.backends.test.EmailBackend'


@pytest.fixture
def inactive_abc_user_registration_link(inactive_abc_user, alice_full_admin):
    return UserRegistrationLink.objects.create(
        user=inactive_abc_user,
        author=alice_full_admin,
        association=alice_full_admin.association,
        expiration_date=timezone.now() + datetime.timedelta(days=alice_full_admin.association.registration_link_life),
    )


@pytest.fixture
def expired_abc_user_registration_link(abc_user, alice_full_admin):
    return UserRegistrationLink.objects.create(
        user=abc_user,
        author=alice_full_admin,
        association=alice_full_admin.association,
        expiration_date=timezone.now() - datetime.timedelta(days=alice_full_admin.association.registration_link_life),
    )


@pytest.fixture
def inactive_xyz_user_registration_link(inactive_xyz_user, xyz_user):
    return UserRegistrationLink.objects.create(
        user=inactive_xyz_user,
        author=xyz_user,
        association=xyz_user.association,
        expiration_date=timezone.now() + datetime.timedelta(days=xyz_user.association.registration_link_life),
    )


@pytest.fixture
def active_abc_user_password_reset_link(abc_user):
    return PasswordResetLink.objects.create(
        user=abc_user,
        association=abc_user.association,
    )


@pytest.fixture
def expired_abc_user_password_reset_link(abc_user):
    link = PasswordResetLink.objects.create(
        user=abc_user,
        association=abc_user.association,
    )
    link.expiration_date = timezone.now() - datetime.timedelta(days=1)
    PasswordResetLink.objects.filter(id=link.id).update(
        expiration_date=timezone.now() - datetime.timedelta(days=1)
    )
    link.refresh_from_db()
    return link


