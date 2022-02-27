from django.urls import reverse
from rest_framework import status

from apps.payments.models import MembershipPaymentSatus
from apps.profiles import roles
from tests import ActMixin


class TestMembershipPaymentsViewSet(ActMixin):

    @staticmethod
    def get_list_url(user):
        return reverse('membership-payments-list', kwargs={'user_pk': str(user.id)})

    @staticmethod
    def detail_url(uu_id):
        return reverse('users-detail', args=(str(uu_id), ))

    def test_an_unauthenticated_user_cannot_list_any_membership_payment(self, base_client, abc_user, user_alice):
        self.act(self.get_list_url(abc_user), base_client, method='get', status_code=status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_regular_user_cannot_add_a_membership_payment(self, authenticated_abc_user_client, abc_user):
        self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client, data={'amount': 10.5},
            method='post',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_cannot_provide_a_negative_payment_amount(self, authenticated_abc_user_client,
                                                      abc_user, user_alice, abc_payments_type):
        abc_user.add_roles(roles.PAYMENT_MANAGER)

        response_data = self.act(
            self.get_list_url(user_alice),
            authenticated_abc_user_client,
            data={
                'amount': -10.5,
                'membership_payment_type_id': str(abc_payments_type[1].id)
            },
            method='post',
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()

        assert response_data['errors'][0]['detail'] == 'Should provide a positive value'

    def test_authenticated_full_admin_can_add_a_user_membership_payment(self, authenticated_abc_user_client, abc_user,
                                                                        user_alice, abc_payments_type):
        abc_user.add_roles(roles.FULL_ADMIN)

        self.act(
            self.get_list_url(user_alice),
            authenticated_abc_user_client,
            data={
                'amount': 10.5,
                'membership_payment_type_id': str(abc_payments_type[0].id)
            },
            method='post',
            status_code=status.HTTP_201_CREATED
        )

    def test_authenticated_payment_manager_can_add_a_user_membership_payment(self, authenticated_abc_user_client,
                                                                             abc_user, user_alice, abc_payments_type):
        abc_user.add_roles(roles.PAYMENT_MANAGER)

        self.act(
            self.get_list_url(user_alice),
            authenticated_abc_user_client,
            data={
                'amount': 10.5,
                'membership_payment_type_id': str(abc_payments_type[1].id)
            },
            method='post',
            status_code=status.HTTP_201_CREATED
        )

    def test_authenticated_payment_manager_can_add_a_user_cost_payment_type(self, authenticated_abc_user_client,
                                                                            abc_user, user_alice, abc_payments_type):
        abc_user.add_roles(roles.PAYMENT_MANAGER)

        response_data = self.act(
            self.get_list_url(user_alice),
            authenticated_abc_user_client,
            data={
                'amount': 10.5,
                'payment_type': 'COST',
                'membership_payment_type_id': str(abc_payments_type[1].id)
            },
            method='post',
            status_code=status.HTTP_201_CREATED
        ).json()
        assert response_data['data']['attributes']['amount'] == -10.5
        assert response_data['data']['attributes']['payment_type'] == 'COST'

    def test_authenticated_full_admin_cannot_modify_a_membership_payment(self, authenticated_abc_user_client, abc_user,
                                                                         abc_user_assurance_payment):
        abc_user.add_roles(roles.FULL_ADMIN)

        self.act(
            f'{self.get_list_url(abc_user)}/{str(abc_user_assurance_payment.id)}',
            authenticated_abc_user_client,
            data={
                'amount': 25,
            },
            method='patch',
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_authenticated_full_admin_cannot_delete_a_membership_payment(self, authenticated_abc_user_client, abc_user,
                                                                         abc_user_assurance_payment):
        abc_user.add_roles(roles.FULL_ADMIN)

        self.act(
            f'{self.get_list_url(abc_user)}/{str(abc_user_assurance_payment.id)}',
            authenticated_abc_user_client,
            method='delete',
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_authenticated_user_cannot_modify_his_membership_payments(self, authenticated_abc_user_client, abc_user,
                                                                      abc_user_assurance_payment):
        assert not abc_user.is_admin

        self.act(
            f'{self.get_list_url(abc_user)}/{str(abc_user_assurance_payment.id)}',
            authenticated_abc_user_client,
            data={
                'amount': 25,
            },
            method='patch',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_authenticated_user_cannot_read_someone_else_membership_payment(self, authenticated_abc_user_client,
                                                                            abc_user, user_alice,
                                                                            abc_user_assurance_payment):
        assert not abc_user.is_admin

        self.act(
            f'{self.get_list_url(user_alice)}/{str(abc_user_assurance_payment.id)}',
            authenticated_abc_user_client,
            method='get',
            status_code=status.HTTP_404_NOT_FOUND
        )

    def test_authenticated_user_can_list_only_his_membership_payments(self, authenticated_abc_user_client, abc_user,
                                                                      abc_user_assurance_payment,
                                                                      abc_user_inscription_payment,
                                                                      xyz_user_membership_payment):
        assert not abc_user.is_admin

        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client,
            method='get',
            status_code=status.HTTP_200_OK
        ).json()

        assert len(response_data['data']) == 2
        for payment in response_data['data']:
            relationships = payment['relationships']
            assert relationships['association']['data']['id'] == str(abc_user.association_id)
            assert relationships['user']['data']['id'] == str(abc_user.id)

    def test_authenticated_full_admin_can_list_a_user_membership_payments(self, authenticated_alice_user_client,
                                                                          abc_user, alice_full_admin,
                                                                          abc_user_assurance_payment,
                                                                          abc_user_inscription_payment,
                                                                          xyz_user_membership_payment):
        assert not abc_user.is_admin
        assert alice_full_admin.is_admin

        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_alice_user_client,
            method='get',
            status_code=status.HTTP_200_OK
        ).json()

        assert len(response_data['data']) == 2
        for payment in response_data['data']:
            relationships = payment['relationships']
            assert relationships['association']['data']['id'] == str(abc_user.association_id)
            assert relationships['user']['data']['id'] == str(abc_user.id)
