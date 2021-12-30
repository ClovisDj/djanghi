import datetime

import pytest
from django.utils import timezone

from apps.profiles.models import UserRegistrationLink


@pytest.fixture
def inactive_abc_user_registration_link(inactive_abc_user, alice_full_admin):
    return UserRegistrationLink.objects.create(
        user=inactive_abc_user,
        author=alice_full_admin,
        association=alice_full_admin.association,
        expiration_date=timezone.now() + datetime.timedelta(days=alice_full_admin.association.registration_link_life),
    )
