import pytest
from rest_framework.test import APIClient

from apps.associations.models import Association


@pytest.fixture(scope='session')
def base_client():
    return APIClient()


@pytest.fixture
def auth_client(base_client, user):
    base_client.force_authenticate(user=user)
    return base_client


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
