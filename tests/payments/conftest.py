import pytest

from apps.payments.models import MembershipPayment


@pytest.fixture
def abc_user_inscription_payment(abc_user, user_alice, abc_payments_type):
    return MembershipPayment.objects.create(
        amount=15.5,
        user=abc_user,
        author=user_alice,
        association=abc_user.association,
        membership_payment_type=abc_payments_type[0]
    )


@pytest.fixture
def abc_user_assurance_cost(abc_user, user_alice, abc_payments_type):
    return MembershipPayment.objects.create(
        amount=150,
        user=abc_user,
        author=user_alice,
        association=abc_user.association,
        payment_type=MembershipPayment.COST,
        membership_payment_type=abc_payments_type[1]
    )


@pytest.fixture
def abc_user_membership_payment(abc_user, user_alice, abc_payments_type):
    return MembershipPayment.objects.create(
        amount=80,
        user=abc_user,
        author=user_alice,
        association=abc_user.association,
        membership_payment_type=abc_payments_type[2]
    )


@pytest.fixture
def xyz_user_membership_payment(xyz_user, inactive_xyz_user, xyz_payments_type):
    return MembershipPayment.objects.create(
        amount=15.5,
        user=inactive_xyz_user,
        author=xyz_user,
        association=xyz_user.association,
        membership_payment_type=xyz_payments_type[2]
    )
