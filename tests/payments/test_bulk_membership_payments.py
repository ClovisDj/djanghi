from django.urls import reverse
from rest_framework import status

from apps.profiles import roles
from apps.profiles.models import User
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

    def test_by_default_bulk_membership_payments_required_user_ids(self, authenticated_alice_user_client,
                                                                   alice_full_admin, abc_bulk_payments_data):
        abc_bulk_payments_data['user_ids'] = []
        abc_bulk_payments_data['for_all_users'] = False

        response = self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=abc_bulk_payments_data,
            method='post',
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()

        errors = response['errors']
        assert errors[0]['detail'] == 'Should Provide at least one valid user'
        assert errors[0]['source']['pointer'].split('/')[-1] == 'user_ids'

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

    def test_authenticated_full_admin_can_bulk_add_membership_payment_to_all_of_his_association_users(
            self, authenticated_alice_user_client, alice_full_admin, abc_bulk_payments_data):

        abc_bulk_payments_data['user_ids'] = []
        abc_bulk_payments_data['for_all_users'] = True
        abc_active_users_count = User.objects.filter(association=alice_full_admin.association, is_active=True).count()

        self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=abc_bulk_payments_data,
            method='post',
            status_code=status.HTTP_201_CREATED
        )

        assert MembershipPayment.objects.filter(
            association=alice_full_admin.association,
            note=abc_bulk_payments_data['note']
        ).count() == abc_active_users_count
