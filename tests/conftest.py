import copy

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.associations.models import Association, MemberContributionField
from apps.payments.models import MembershipPayment
from apps.profiles.models import User
from apps.profiles.roles import FULL_ADMIN


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
        'is_registered': True,
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
def third_abc_user(user_create_data, association_abc):
    data = copy.deepcopy(user_create_data)
    data['email'] = 'abc.user.3@abc.com'
    data['first_name'] = 'Richard'
    data['last_name'] = 'Kenfack'
    data['association_id'] = association_abc.id
    return User.objects.create_user(
        'abc.user.3@abc.com',
        **data
    )


@pytest.fixture
def user_alice(user_create_data, association_abc):
    data = copy.deepcopy(user_create_data)
    data['email'] = 'alice@abc.com'
    data['first_name'] = 'alice'
    data['last_name'] = 'Johnson'
    data['association_id'] = association_abc.id
    return User.objects.create_user(
        'alice@abc.com',
        **data
    )


@pytest.fixture
def xyz_user_alice(user_create_data, association_xyz):
    data = copy.deepcopy(user_create_data)
    data['email'] = 'alice@abc.com'
    data['first_name'] = 'alice'
    data['last_name'] = 'Johnson'
    data['association_id'] = association_xyz.id
    return User.objects.create_user(
        'alice@abc.com',
        **data
    )


@pytest.fixture
def inactive_abc_user(user_create_data, association_abc):
    data = copy.deepcopy(user_create_data)
    data['email'] = 'abc.user.2@abc.com'
    data['first_name'] = 'Ian'
    data['last_name'] = 'Clay'
    data['association_id'] = association_abc.id
    data['is_active'] = False
    data['is_registered'] = False
    return User.objects.create_user(
        'abc.user.1@abc.com',
        **data
    )


@pytest.fixture
def xyz_user(user_create_data, association_xyz):
    user_create_data['email'] = 'xyz.user.1@xyz.com'
    user_create_data['association_id'] = association_xyz.id
    return User.objects.create_user(
        user_create_data['email'],
        **user_create_data
    )


@pytest.fixture
def inactive_xyz_user(user_create_data, association_xyz):
    user_create_data['email'] = 'xyz.user.2@xyz.com'
    user_create_data['association_id'] = association_xyz.id
    user_create_data['is_active'] = False
    user_create_data['is_registered'] = False
    return User.objects.create_user(
        user_create_data['email'],
        **user_create_data
    )


@pytest.fixture
def authenticated_abc_user_client(base_client, abc_user):
    abc_user_token = RefreshToken.for_user(abc_user).access_token
    base_client.credentials(HTTP_AUTHORIZATION=f'JWT {abc_user_token}')
    return base_client


@pytest.fixture
def authenticated_alice_user_client(base_client, user_alice):
    user_alice_token = RefreshToken.for_user(user_alice).access_token
    base_client.credentials(HTTP_AUTHORIZATION=f'JWT {user_alice_token}')
    return base_client


@pytest.fixture
def alice_full_admin(user_alice):
    user_alice.add_roles(*[FULL_ADMIN])
    return user_alice


@pytest.fixture
def abc_payments_type(association_abc):
    payment_names = ('Inscription', 'Assurance', 'Membership')
    return [
        MemberContributionField.objects.create(
            name=name,
            association=association_abc
        )
        for name in payment_names
    ]


@pytest.fixture
def xyz_payments_type(association_xyz):
    payment_names = ('Inscription', 'Assurance', 'Membership')
    return [
        MemberContributionField.objects.create(
            name=name,
            association=association_xyz
        )
        for name in payment_names
    ]


@pytest.fixture
def abc_user_assurance_payment(abc_user, user_alice, abc_payments_type):
    return MembershipPayment.objects.create(
        amount=200,
        user=abc_user,
        author=user_alice,
        association=abc_user.association,
        membership_payment_type=abc_payments_type[1]
    )
