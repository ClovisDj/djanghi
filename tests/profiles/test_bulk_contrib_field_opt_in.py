from django.urls import reverse
from rest_framework import status

from apps.profiles import roles
from apps.profiles.models import User, UserOptInContributionFields
from apps.payments.models import MembershipPayment
from tests import ActMixin


class TestContribFieldOptInModelViewSet(ActMixin):
    list_url = reverse('profiles_urls:contrib-field-opt-ins-list')

    def test_an_unauthenticated_user_cannot_access_contrib_field_opt_ins_endpoint(self, base_client,
                                                                                  abc_bulk_contrib_opt_in_data):
        self.act(
            self.list_url,
            base_client,
            data=abc_bulk_contrib_opt_in_data,
            method='post',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    def test_authenticated_regular_user_cannot_access_contrib_field_opt_ins_endpoint(self,
                                                                                     authenticated_abc_user_client,
                                                                                     abc_user,
                                                                                     abc_bulk_contrib_opt_in_data):
        self.act(
            self.list_url,
            authenticated_abc_user_client,
            data=abc_bulk_contrib_opt_in_data,
            method='post',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_full_admin_cannot_bulk_opt_in_users_not_in_his_association(self, authenticated_alice_user_client,
                                                                        alice_full_admin, abc_bulk_contrib_opt_in_data,
                                                                        xyz_user, inactive_xyz_user):

        abc_bulk_contrib_opt_in_data['user_ids'] = [str(xyz_user.id), str(inactive_xyz_user.id)]

        response = self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=abc_bulk_contrib_opt_in_data,
            method='post',
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()

        errors = response['errors']
        assert errors[0]['detail'] == 'Should Provide at least one valid user'

    def test_authenticated_payment_manager_cannot_bulk_opt_in_users(self, authenticated_abc_user_client,
                                                                    abc_user, abc_bulk_contrib_opt_in_data):
        abc_user.add_roles(roles.PAYMENT_MANAGER)

        self.act(
            self.list_url,
            authenticated_abc_user_client,
            data=abc_bulk_contrib_opt_in_data,
            method='post',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_authenticated_full_admin_can_bulk_opt_in_users(self, authenticated_alice_user_client, alice_full_admin,
                                                            abc_bulk_contrib_opt_in_data, abc_user, user_alice,
                                                            third_abc_user):

        assert not abc_user.opted_in_contrib_fields.all().exists()
        assert not user_alice.opted_in_contrib_fields.all().exists()
        assert not third_abc_user.opted_in_contrib_fields.all().exists()

        self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=abc_bulk_contrib_opt_in_data,
            method='post',
            status_code=status.HTTP_201_CREATED
        )

        assert abc_user.opted_in_contrib_fields.all().exists()
        assert user_alice.opted_in_contrib_fields.all().exists()
        assert third_abc_user.opted_in_contrib_fields.all().exists()

    def test_a_full_admin_can_bulk_opt_in_user_with_state_approved(self, authenticated_alice_user_client,
                                                                   alice_full_admin,
                                                                   abc_bulk_contrib_opt_in_data, abc_user):

        abc_bulk_contrib_opt_in_data['state'] = UserOptInContributionFields.APPROVED

        self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=abc_bulk_contrib_opt_in_data,
            method='post',
            status_code=status.HTTP_201_CREATED
        )
        assert abc_user.opted_in_contrib_fields.count() == 1
        assert abc_user.opted_in_contrib_fields.all()[0].state == UserOptInContributionFields.APPROVED

