import pytest
from django.urls import reverse
from rest_framework import status

from apps.profiles import roles
from apps.profiles.models import UserOptInContributionFields
from tests import ActMixin


class TestUserPaymentOptIn(ActMixin):
    @staticmethod
    def get_list_url(user):
        return reverse('payment-opt-in-list', kwargs={'user_pk': str(user.id)})

    def test_an_unauthenticated_user_cannot_opt_in(self, base_client, abc_user, abc_payments_type):
        self.act(
            self.get_list_url(abc_user),
            base_client,
            data={'requested_field_id': str(abc_payments_type[0].id)},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    def test_an_authenticated_user_cannot_opt_in_for_a_non_existing_field_in_his_association(self, abc_user,
                                                                                             authenticated_abc_user_client,
                                                                                             xyz_payments_type):
        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client,
            data={'requested_field_id': "sdnbsdoj-wgmsdibk-emgvdsovi-90dw8uv"},
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()
        assert response_data['errors'][0]['detail'] == 'Must be a valid UUID.'

    def test_an_authenticated_user_cannot_opt_in_to_a_payment_not_in_his_association(self, abc_user,
                                                                                     authenticated_abc_user_client,
                                                                                     xyz_payments_type):
        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client,
            data={'requested_field_id': str(xyz_payments_type[0].id)},
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()

        assert response_data['errors'][0]['detail'] == 'This payment field does not exists!'

    def test_an_authenticated_user_cannot_opt_in_to_an_archived_contrib_field(self, abc_user,
                                                                              authenticated_abc_user_client,
                                                                              abc_payments_type):
        abc_payments_type[0].archived = True
        abc_payments_type[0].save()
        assert abc_payments_type[0].archived

        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client,
            data={'requested_field_id': str(abc_payments_type[0].id)},
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()

        assert response_data['errors'][0]['detail'] == 'This payment field does not exists!'

    def test_an_authenticated_user_cannot_opt_in_another_user_to_a_payment(self, abc_user, user_alice,
                                                                           authenticated_abc_user_client,
                                                                           abc_payments_type):
        response_data = self.act(
            self.get_list_url(user_alice),
            authenticated_abc_user_client,
            data={'requested_field_id': str(abc_payments_type[0].id)},
            status_code=status.HTTP_403_FORBIDDEN
        ).json()

        assert response_data['errors'][0]['detail'] == 'You do not have permission to perform this action.'

    def test_an_authenticated_user_cannot_opt_int_to_a_non_opt_in_payment(self, abc_user, user_alice,
                                                                          authenticated_abc_user_client,
                                                                          abc_payments_type):
        assert not abc_payments_type[0].member_can_opt_in

        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client,
            data={'requested_field_id': str(abc_payments_type[0].id)},
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()

        assert response_data['errors'][0]['detail'] == 'Cannot opt-in to a non opt-in payment type.'

    def test_an_authenticated_user_cannot_opt_int_with_a_state_other_than_requested(self, abc_user, user_alice,
                                                                                    authenticated_abc_user_client,
                                                                                    abc_payments_type):
        assert abc_payments_type[1].member_can_opt_in

        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client,
            data={
                'requested_field_id': str(abc_payments_type[1].id),
                'state': UserOptInContributionFields.IN_PROCESS
            },
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()

        assert response_data['errors'][0]['detail'] == "Cannot create an opt-in with a state other than 'REQUESTED'"

    def test_an_authenticated_user_can_opt_in_to_a_valid_contribution_field(self, abc_user, user_alice,
                                                                            authenticated_abc_user_client,
                                                                            abc_payments_type):
        abc_payments_type[0].member_can_opt_in = True
        abc_payments_type[0].save()
        assert abc_payments_type[0].member_can_opt_in

        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client,
            data={'requested_field_id': str(abc_payments_type[0].id)},
            status_code=status.HTTP_201_CREATED
        ).json()['data']

        attributes = response_data['attributes']
        relationships = response_data['relationships']
        assert attributes['state'] == UserOptInContributionFields.REQUESTED
        assert attributes['state'] == UserOptInContributionFields.REQUESTED
        assert relationships['contrib_field']['data'] is None
        assert relationships['approved_by']['data'] is None

    def test_a_payment_manager_cannot_opt_in_a_user_to_valid_contribution_field(self, abc_user, user_alice,
                                                                                authenticated_alice_user_client,
                                                                                abc_payments_type):
        user_alice.add_roles(roles.PAYMENT_MANAGER)

        assert user_alice.is_payment_manager
        assert abc_payments_type[1].member_can_opt_in

        self.act(
            self.get_list_url(abc_user),
            authenticated_alice_user_client,
            data={'requested_field_id': str(abc_payments_type[1].id)},
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_a_full_admin_can_opt_in_a_user_to_valid_contribution_field(self, abc_user, alice_full_admin,
                                                                        authenticated_alice_user_client,
                                                                        abc_payments_type):
        assert abc_payments_type[1].member_can_opt_in

        self.act(
            self.get_list_url(abc_user),
            authenticated_alice_user_client,
            data={'requested_field_id': str(abc_payments_type[1].id)},
            status_code=status.HTTP_201_CREATED
        )

    @pytest.mark.skip(reason="Flaky when run with other tests")
    def test_unique_contribution_field_opt_in_by_user(self, abc_user, abc_user_insurance_opt_in,
                                                      authenticated_abc_user_client,
                                                      abc_payments_type):

        assert abc_payments_type[1].member_can_opt_in
        assert abc_user_insurance_opt_in.contrib_field_id == abc_payments_type[1].id

        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client,
            data={'requested_field_id': str(abc_payments_type[1].id)},
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()

        assert response_data['errors'][0]['detail'] == 'An opt-in request for this payment already exists'

    def test_an_authenticated_user_cannot_modify_his_payment_opt_in_object(self, abc_user, abc_user_insurance_opt_in,
                                                                           authenticated_alice_user_client,
                                                                           abc_payments_type):
        self.act(
            f'{self.get_list_url(abc_user)}/{str(abc_user_insurance_opt_in.id)}',
            authenticated_alice_user_client,
            method='patch',
            data={'state': UserOptInContributionFields.APPROVED},
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_a_payment_manager_cannot_modify_his_payment_opt_in_object(self, abc_user, user_alice,
                                                                       abc_user_insurance_opt_in,
                                                                       authenticated_alice_user_client,
                                                                       abc_payments_type):
        user_alice.add_roles(roles.PAYMENT_MANAGER)
        assert user_alice.is_payment_manager

        self.act(
            f'{self.get_list_url(abc_user)}/{str(abc_user_insurance_opt_in.id)}',
            authenticated_alice_user_client,
            method='patch',
            data={'state': UserOptInContributionFields.APPROVED},
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_a_full_admin_can_modify_a_user_payment_opt_in_object(self, abc_user, alice_full_admin,
                                                                  abc_user_insurance_opt_in,
                                                                  authenticated_alice_user_client,
                                                                  abc_payments_type):
        assert alice_full_admin.is_full_admin
        assert abc_user_insurance_opt_in.state == UserOptInContributionFields.APPROVED

        response_data = self.act(
            f'{self.get_list_url(abc_user)}/{str(abc_user_insurance_opt_in.id)}',
            authenticated_alice_user_client,
            method='patch',
            data={'state': UserOptInContributionFields.DECLINED},
            status_code=status.HTTP_200_OK
        ).json()['data']

        assert response_data['attributes']['state'] == UserOptInContributionFields.DECLINED

    def test_a_full_admin_can_approve_user_payment_opt_in_request(self, abc_user, alice_full_admin,
                                                                  abc_user_insurance_opt_in,
                                                                  authenticated_alice_user_client,
                                                                  abc_payments_type):

        abc_user_insurance_opt_in.state = UserOptInContributionFields.IN_PROCESS
        abc_user_insurance_opt_in.contrib_field_id = None
        abc_user_insurance_opt_in.save()

        assert abc_user_insurance_opt_in.contrib_field is None
        assert abc_user_insurance_opt_in.approved_by is None

        response_data = self.act(
            f'{self.get_list_url(abc_user)}/{str(abc_user_insurance_opt_in.id)}',
            authenticated_alice_user_client,
            method='patch',
            data={'state': UserOptInContributionFields.APPROVED},
            status_code=status.HTTP_200_OK
        ).json()

        attributes = response_data['data']['attributes']
        relationships = response_data['data']['relationships']
        assert attributes['state'] == UserOptInContributionFields.APPROVED
        assert relationships['contrib_field']['data']['id'] == str(abc_payments_type[1].id)
        assert relationships['approved_by']['data']['id'] == str(alice_full_admin.id)

    def test_an_authenticated_user_can_list_his_payment_opt_in_objects(self, abc_user, abc_user_insurance_opt_in,
                                                                       authenticated_abc_user_client,
                                                                       user_alice_insurance_opt_in,
                                                                       xyz_user_insurance_opt_in,
                                                                       abc_payments_type):
        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client,
            method='get',
            status_code=status.HTTP_200_OK
        ).json()['data']

        assert len(response_data) == 1
        assert response_data[0]['relationships']['user']['data']['id'] == str(abc_user.id)

    def test_full_admin_can_list_nested_user_opt_in_objects(self, abc_user, abc_user_insurance_opt_in,
                                                            alice_full_admin,
                                                            authenticated_alice_user_client,
                                                            user_alice_insurance_opt_in,
                                                            xyz_user_insurance_opt_in,
                                                            abc_payments_type):

        response_data = self.act(
            self.get_list_url(abc_user),
            authenticated_alice_user_client,
            method='get',
            status_code=status.HTTP_200_OK
        ).json()['data']

        assert len(response_data) == 1
        assert response_data[0]['relationships']['user']['data']['id'] == str(abc_user.id)

    def test_an_authenticated_user_cannot_delete_payment_opt_in_objects(self, abc_user, abc_user_insurance_opt_in,
                                                                        authenticated_abc_user_client,
                                                                        abc_payments_type):
        self.act(
            f'{self.get_list_url(abc_user)}/{str(abc_user_insurance_opt_in.id)}',
            authenticated_abc_user_client,
            method='delete',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_full_admin_can_delete_a_user_payment_opt_in_objects(self, abc_user, abc_user_insurance_opt_in,
                                                                 alice_full_admin,
                                                                 authenticated_alice_user_client,
                                                                 abc_payments_type):
        to_delete_opt_in_id = str(abc_user_insurance_opt_in.id)
        self.act(
            f'{self.get_list_url(abc_user)}/{to_delete_opt_in_id}',
            authenticated_alice_user_client,
            method='delete',
            status_code=status.HTTP_204_NO_CONTENT
        )

        assert not UserOptInContributionFields.objects.filter(id=to_delete_opt_in_id).exists()
