from django.urls import reverse
from rest_framework import status

from tests import ActMixin


class TestMembershipPaymentsStatusViewSet(ActMixin):

    @staticmethod
    def get_list_url(user):
        return reverse('membership-payments-status-list', kwargs={'user_pk': str(user.id)})

    def test_an_unauthenticated_user_cannot_list_any_payment_status(self, base_client, abc_user, user_alice):
        self.act(
            self.get_list_url(abc_user),
            base_client,
            method='get',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    def test_authenticated_regular_user_cannot_add_a_payments_status(self, authenticated_abc_user_client, abc_user):
        self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client, data={'amount': 10.5},
            method='post',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_authenticated_regular_user_cannot_read_someone_else_payments_status(self, authenticated_alice_user_client,
                                                                                 abc_user, xyz_user_membership_payment,
                                                                                 abc_user_assurance_payment):
        self.act(
            self.get_list_url(abc_user),
            authenticated_alice_user_client,
            method='get',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_authenticated_full_admin_cannot_add_a_payments_status(self, authenticated_alice_user_client, abc_user,
                                                                   alice_full_admin):
        self.act(
            self.get_list_url(abc_user),
            authenticated_alice_user_client, data={'amount': 10.5},
            method='post',
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_an_admin_cannot_another_association_user_payments_status(self, authenticated_alice_user_client,
                                                                      alice_full_admin, xyz_user,
                                                                      xyz_user_membership_payment,
                                                                      abc_user_assurance_payment):
        self.act(
            self.get_list_url(xyz_user),
            authenticated_alice_user_client,
            method='get',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_authenticated_full_admin_can_read_a_user_payments_status(self, authenticated_alice_user_client, abc_user,
                                                                      alice_full_admin, abc_user_inscription_payment,
                                                                      abc_user_assurance_payment,
                                                                      abc_user_assurance_cost,
                                                                      abc_user_membership_payment):
        response = self.act(
            self.get_list_url(abc_user),
            authenticated_alice_user_client, data={'amount': 10.5},
            method='get',
            status_code=status.HTTP_200_OK
        ).json()

        for included in response['included']:
            included_id = included['id']
            for status_data in response['data']:
                if status_data['relationships']['membership_payment_type']['data']['id'] == included_id:
                    if included['attributes']['name'] == 'Inscription':
                        assert status_data['attributes']['current_value'] == abc_user_inscription_payment.amount

                    if included['attributes']['name'] == 'Assurance':
                        assert status_data['attributes']['current_value'] == \
                               abc_user_assurance_payment.amount + abc_user_assurance_cost.amount

                    if included['attributes']['name'] == 'Membership':
                        assert status_data['attributes']['current_value'] == abc_user_membership_payment.amount

    def test_authenticated_regular_user_can_read_a_user_payments_status(self, authenticated_abc_user_client, abc_user,
                                                                        alice_full_admin, abc_user_inscription_payment,
                                                                        abc_user_assurance_payment,
                                                                        abc_user_assurance_cost,
                                                                        abc_user_membership_payment):
        response = self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client, data={'amount': 10.5},
            method='get',
            status_code=status.HTTP_200_OK
        ).json()

        for included in response['included']:
            included_id = included['id']
            for status_data in response['data']:
                if status_data['relationships']['membership_payment_type']['data']['id'] == included_id:
                    if included['attributes']['name'] == 'Inscription':
                        assert status_data['attributes']['current_value'] == abc_user_inscription_payment.amount

                    if included['attributes']['name'] == 'Assurance':
                        assert status_data['attributes']['current_value'] == \
                               abc_user_assurance_payment.amount + abc_user_assurance_cost.amount

                    if included['attributes']['name'] == 'Membership':
                        assert status_data['attributes']['current_value'] == abc_user_membership_payment.amount