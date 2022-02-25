import pytest

from apps.associations.models import MemberContributionField


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

