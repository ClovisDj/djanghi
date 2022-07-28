from django.urls import reverse
from rest_framework import status

from apps.profiles import roles
from apps.profiles.roles import PAYMENT_MANAGER
from tests import ActMixin


class TestAssociationContributionField(ActMixin):
    list_url = reverse('associations_urls:contribution-fields-list')

    @staticmethod
    def detail_url(uu_id):
        return reverse('associations_urls:contribution-fields-detail', args=(str(uu_id), ))

    @property
    def create_data(self):
        return {
            'name': 'Recouvrement',
        }

    def test_an_unauthenticated_user_cannot_list_contribution_fields(self, base_client):
        self.act(self.list_url, base_client, method='get',
                 status_code=status.HTTP_401_UNAUTHORIZED)

    def test_an_authenticated_regular_user_can_list_his_association_contribution_fields(self,
                                                                                        authenticated_abc_user_client,
                                                                                        abc_payments_type,
                                                                                        xyz_payments_type):
        abc_contrib_field_ids = [str(contrib.id) for contrib in abc_payments_type]

        response_data = self.act(
            self.list_url,
            authenticated_abc_user_client,
            method='get',
            status_code=status.HTTP_200_OK
        ).json()

        assert len(abc_payments_type) == len(response_data['data'])
        for contrib_field in response_data['data']:
            assert contrib_field['id'] in abc_contrib_field_ids

    def test_a_payment_manager_should_have_read_access_to_contribution_fields(self, authenticated_abc_user_client,
                                                                              abc_user, abc_payments_type):
        abc_user.add_roles(roles.PAYMENT_MANAGER)
        self.act(self.list_url, authenticated_abc_user_client, method='get', status_code=status.HTTP_200_OK)

    def test_full_admin_can_list_his_association_contribution_fields(self, authenticated_alice_user_client,
                                                                     alice_full_admin, abc_payments_type,
                                                                     xyz_payments_type):
        response_data = self.act(
            self.list_url,
            authenticated_alice_user_client,
            method='get',
            status_code=status.HTTP_200_OK
        ).json()

        response_ids_set = {item['id'] for item in response_data['data']}
        assert response_ids_set == {str(obj.id) for obj in abc_payments_type}

    def test_full_admin_can_add_an_association_contribution_fields(self, authenticated_alice_user_client,
                                                                   alice_full_admin):
        self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=self.create_data,
            method='post',
            status_code=status.HTTP_201_CREATED
        )

    def test_max_active_contrib_fields_allowed_by_association(self, authenticated_alice_user_client, alice_full_admin,
                                                              abc_payments_type, xyz_payments_type, settings):
        settings.MAX_PAGE_SIZE = 3

        response = self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=self.create_data,
            method='post',
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()['errors'][0]

        assert response["detail"] == f'Max {settings.MAX_PAGE_SIZE} active payment fields allowed'

    def test_contribution_field_name_should_be_unique_for_an_association(self, authenticated_alice_user_client,
                                                                         abc_payments_type, alice_full_admin):
        error_data = self.act(
            self.list_url,
            authenticated_alice_user_client,
            data={'name': 'Inscription'},
            method='post',
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()['errors'][0]

        assert error_data['detail'] == 'A contribution field with name: Inscription, already exists'

    def test_contribution_field_name_should_be_unique_for_an_in_update_action_association(
            self, authenticated_alice_user_client, abc_payments_type, alice_full_admin):

        error_data = self.act(
            f'{self.list_url}/{str(abc_payments_type[1].id)}',
            authenticated_alice_user_client,
            data={'name': 'Inscription'},
            method='patch',
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()['errors'][0]

        assert error_data['detail'] == 'A contribution field with name: Inscription, already exists'

    def test_full_admin_can_update_his_association_contribution_field(self, authenticated_alice_user_client,
                                                                      abc_payments_type, alice_full_admin):

        response_data = self.act(
            f'{self.list_url}/{str(abc_payments_type[1].id)}',
            authenticated_alice_user_client,
            data={
                'is_required': False,
                'required_amount': 145.5,
                'member_can_opt_in': True,
            },
            method='patch',
            status_code=status.HTTP_200_OK
        ).json()['data']['attributes']

        assert not response_data['is_required']
        assert response_data['member_can_opt_in']
        assert response_data['required_amount'] == 145.5

    def test_full_admin_cannot_delete_a_contribution_field_in_use(self, authenticated_alice_user_client,
                                                                  abc_payments_type, abc_user_assurance_payment,
                                                                  alice_full_admin):
        error_data = self.act(
            f'{self.list_url}/{str(abc_payments_type[1].id)}',
            authenticated_alice_user_client,
            method='delete',
            status_code=status.HTTP_400_BAD_REQUEST
        ).json()['errors'][0]

        assert error_data['detail'] == 'This contribution field is already in use and cannot be deleted'

    def test_full_admin_can_delete_a_non_in_use_contribution_field(self, authenticated_alice_user_client,
                                                                   abc_payments_type, alice_full_admin):
        self.act(
            f'{self.list_url}/{str(abc_payments_type[1].id)}',
            authenticated_alice_user_client,
            method='delete',
            status_code=status.HTTP_204_NO_CONTENT
        )

    def test_a_regular_user_cannot_archive_a_contrib_field(self, authenticated_abc_user_client, abc_payments_type):
        self.act(
            f'{self.detail_url(abc_payments_type[1].id)}/archive',
            authenticated_abc_user_client,
            method='post',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_a_non_full_admin_user_cannot_archive_a_contrib_field(self, authenticated_abc_user_client,
                                                                  abc_payments_type,
                                                                  user_alice):
        user_alice.add_roles(PAYMENT_MANAGER)

        assert user_alice.is_admin
        assert not user_alice.is_full_admin

        self.act(
            f'{self.detail_url(abc_payments_type[1].id)}/archive',
            authenticated_abc_user_client,
            method='post',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_only_a_full_admin_user_can_archive_a_contrib_field(self, authenticated_alice_user_client,
                                                                abc_payments_type, alice_full_admin):
        assert alice_full_admin.is_full_admin

        self.act(
            f'{self.detail_url(abc_payments_type[1].id)}/archive',
            authenticated_alice_user_client,
            method='post',
            status_code=status.HTTP_204_NO_CONTENT
        )

        abc_payments_type[1].refresh_from_db()
        assert abc_payments_type[1].archived
        assert abc_payments_type[1].archived_by_id == alice_full_admin.id

    def test_a_regular_user_cannot_list_an_archived_contribution_field(self, authenticated_abc_user_client,
                                                                       abc_payments_type):
        abc_payments_type[0].archived = True
        abc_payments_type[0].save()

        response_data = self.act(
            self.list_url,
            authenticated_abc_user_client,
            method='get',
            status_code=status.HTTP_200_OK
        ).json()

        assert len(response_data['data']) == len(abc_payments_type) - 1
        for contrib in response_data['data']:
            assert contrib['id'] != str(abc_payments_type[0].id)
