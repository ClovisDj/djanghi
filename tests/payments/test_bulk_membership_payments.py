from django.urls import reverse
from rest_framework import status

from apps.profiles import roles
from apps.payments.models import MembershipPayment
from tests import ActMixin


class TestBulkMembershipPaymentsViewSet(ActMixin):
    list_url = reverse('payments_urls:bulk-payments-list')

    def test_an_unauthenticated_user_cannot_access_bulk_membership_payments_endpoint(self, base_client,
                                                                                     abc_bulk_payments_data):
        self.act(
            self.list_url,
            base_client,
            data=abc_bulk_payments_data,
            method='post',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    def test_authenticated_regular_user_cannot_bulk_add_membership_payments(self, authenticated_abc_user_client,
                                                                            abc_user, abc_bulk_payments_data):
        self.act(
            self.list_url,
            authenticated_abc_user_client,
            data=abc_bulk_payments_data,
            method='post',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_authenticated_full_admin_can_bulk_add_membership_payments(self, authenticated_alice_user_client,
                                                                       alice_full_admin, abc_bulk_payments_data):
        self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=abc_bulk_payments_data,
            method='post',
            status_code=status.HTTP_201_CREATED
        )

    def test_authenticated_full_admin_cannot_bulk_add_membership_payments_for_user_in_another_association(
            self, authenticated_alice_user_client, alice_full_admin, abc_user, abc_bulk_payments_data, xyz_user):

        abc_bulk_payments_data['user_ids'].append(str(xyz_user.id))

        assert not xyz_user.membership_payments.exists()

        self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=abc_bulk_payments_data,
            method='post',
            status_code=status.HTTP_201_CREATED
        )

        assert not xyz_user.membership_payments.exists()
        assert abc_user.membership_payments.filter(note=abc_bulk_payments_data['note']).exists()

    def test_authenticated_payment_manager_can_add_a_user_membership_payment(self, authenticated_abc_user_client,
                                                                             abc_user, abc_bulk_payments_data):
        abc_user.add_roles(roles.PAYMENT_MANAGER)

        self.act(
            self.list_url,
            authenticated_abc_user_client,
            data=abc_bulk_payments_data,
            method='post',
            status_code=status.HTTP_201_CREATED
        )

    def test_authenticated_payment_manager_can_add_a_user_cost_payment_type(self, authenticated_abc_user_client,
                                                                            abc_user, abc_bulk_payments_data):
        abc_user.add_roles(roles.PAYMENT_MANAGER)

        abc_bulk_payments_data['payment_type'] = MembershipPayment.COST

        self.act(
            self.list_url,
            authenticated_abc_user_client,
            data=abc_bulk_payments_data,
            method='post',
            status_code=status.HTTP_201_CREATED
        )
