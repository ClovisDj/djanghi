import pytest

from apps.profiles.models import User


@pytest.fixture
def user_alice(user_create_data, association_abc):
    user_create_data['email'] = 'alice@abc.com'
    user_create_data['first_name'] = 'alice'
    user_create_data['last_name'] = 'Johnson'
    user_create_data['association_id'] = association_abc.id
    return User.objects.create_user(
        'alice@abc.com',
        **user_create_data
    )
