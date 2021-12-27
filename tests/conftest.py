import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.associations.models import Association
from apps.profiles.models import User


@pytest.fixture(scope='session')
def base_client():
    return APIClient()


@pytest.fixture
def association_create_data():
    return {
        'name': '',
        'label': '',
        'contact_email': 'contact@example.com',
        'city': 'Austin',
        'country': 'United States of America',
        'address': '',
        'email_from': ''
    }


@pytest.fixture
def association_abc(association_create_data):
    association_create_data['name'] = 'Association - ABC'
    association_create_data['label'] = 'Abc'
    association_create_data['email_from'] = 'noreply@abc.com'
    return Association.objects.create(**association_create_data)


@pytest.fixture
def association_xyz(association_create_data):
    association_create_data['name'] = 'Association - xyz'
    association_create_data['label'] = 'XYZ'
    association_create_data['email_from'] = 'noreply@xyz.com'
    return Association.objects.create(**association_create_data)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Special fixture to enable db access to all tests
    """
    pass


@pytest.fixture
def user_create_data():
    return {
        'email': '',
        'password': 'Password123',
        'first_name': 'Paul',
        'last_name': 'Jean',
        'is_active': True,
    }


@pytest.fixture
def abc_user(user_create_data, association_abc):
    user_create_data['email'] = 'abc.user.1@abc.com'
    user_create_data['association_id'] = association_abc.id
    return User.objects.create_user(
        'abc.user.1@abc.com',
        **user_create_data
    )


@pytest.fixture
def inactive_abc_user(user_create_data, association_abc):
    user_create_data['email'] = 'abc.user.2@abc.com'
    user_create_data['association_id'] = association_abc.id
    user_create_data['is_active'] = False
    return User.objects.create_user(
        'abc.user.1@abc.com',
        **user_create_data
    )


@pytest.fixture
def xyz_user(user_create_data, association_xyz):
    user_create_data['email'] = 'xyz.user.1@xyz.com'
    user_create_data['association_id'] = association_xyz.id
    return User.objects.create_user(
        'abc.user.1@abc.com',
        **user_create_data
    )


@pytest.fixture
def authenticated_abc_user_client(base_client, abc_user):
    abc_user_token = RefreshToken.for_user(abc_user).access_token
    base_client.credentials(HTTP_AUTHORIZATION=f'JWT {abc_user_token}')
    return base_client

