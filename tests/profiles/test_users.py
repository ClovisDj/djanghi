from django.urls import reverse
from rest_framework import status

from apps.profiles import roles
from tests import ActMixin


class TestUserModelViewSet(ActMixin):
    list_url = reverse('users-list')

    @staticmethod
    def detail_url(uu_id):
        return reverse('users-detail', args=(str(uu_id), ))

    def test_an_unauthenticated_user_cannot_list_any_users(self, base_client, abc_user, user_alice):
        self.act(self.list_url, base_client, method='get', status_code=status.HTTP_401_UNAUTHORIZED)

    def test_an_authenticated_regular_user_can_list_his_association_users(self, authenticated_abc_user_client,
                                                                          abc_user, user_alice, inactive_abc_user,
                                                                          xyz_user):
        response = self.act(self.list_url, authenticated_abc_user_client, method='get',
                            status_code=status.HTTP_200_OK).json()
        assert len(response['data']) == 2
        for user in response['data']:
            assert user['id'] != str(inactive_abc_user.id)
            assert user['relationships']['association']['data']['id'] != str(xyz_user.association_id)

    def test_an_authenticated_user_cannot_read_other_user_details(self, authenticated_abc_user_client, user_alice):
        self.act(
            self.detail_url(user_alice.id),
            authenticated_abc_user_client,
            method='get',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_an_authenticated_user_can_modify_his_user_data(self, authenticated_abc_user_client, abc_user):
        patch_data = {
            'first_name': 'Clovis',
            'is_registered': False,
            'is_active': False,
            'email': 'cannot.modify@email.com',
        }
        assert abc_user.first_name != patch_data['first_name']
        assert abc_user.is_active
        assert abc_user.is_registered

        response = self.act(
            self.detail_url(abc_user.id),
            authenticated_abc_user_client,
            data=patch_data,
            method='patch',
            status_code=status.HTTP_200_OK
        ).json()

        attributes = response['data']['attributes']
        assert attributes['first_name'] == patch_data['first_name']
        assert attributes['is_active']      # Read only field
        assert attributes['is_registered']  # Read only field

    def test_a_full_admin_can_modify_any_user_data_of_his_association(self, authenticated_alice_user_client, abc_user,
                                                                      alice_full_admin):
        patch_data = {
            'first_name': 'Francis',
            'is_registered': False,
            'is_active': False,
            'email': 'cannot.modify@email.com',
        }
        assert abc_user.first_name != patch_data['first_name']
        assert abc_user.is_active
        assert abc_user.is_registered

        response = self.act(
            self.detail_url(abc_user.id),
            authenticated_alice_user_client,
            data=patch_data,
            method='patch',
            status_code=status.HTTP_200_OK
        ).json()

        attributes = response['data']['attributes']
        assert attributes['first_name'] == patch_data['first_name']
        assert attributes['is_active']      # Read only field
        assert attributes['is_registered']  # Read only field

    def test_only_full_admin_can_deactivate_a_user_of_his_association(self, authenticated_alice_user_client,
                                                                      alice_full_admin, abc_user):
        self.act(
            self.detail_url(abc_user.id),
            authenticated_alice_user_client,
            method='delete',
            status_code=status.HTTP_204_NO_CONTENT
        )

        abc_user.refresh_from_db()
        assert not abc_user.is_active

    def test_a_user_cannot_deactivate_himself(self, authenticated_abc_user_client, abc_user):
        self.act(
            self.detail_url(abc_user.id),
            authenticated_abc_user_client,
            method='delete',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_regular_user_should_not_have_access_to_admin_info_details(self, authenticated_abc_user_client, abc_user):
        attributes = self.act(self.detail_url(abc_user.id), authenticated_abc_user_client, method='get',
                              status_code=status.HTTP_200_OK).json()['data']['attributes']

        assert 'is_admin' not in attributes
        assert 'is_full_admin' not in attributes
        assert 'is_payment_manager' not in attributes

    def test_admin_should_have_access_to_admin_info_details(self, authenticated_alice_user_client, abc_user,
                                                            alice_full_admin):
        attributes = self.act(self.detail_url(abc_user.id), authenticated_alice_user_client, method='get',
                              status_code=status.HTTP_200_OK).json()['data']['attributes']

        assert 'is_admin' in attributes
        assert 'is_full_admin' in attributes
        assert 'is_payment_manager' in attributes

    def test_regular_user_cannot_add_a_role(self, authenticated_alice_user_client, user_alice, abc_user):
        user_alice.roles.clear()
        assert not user_alice.is_admin

        self.act(
            f'{self.detail_url(abc_user.id)}/admin',
            authenticated_alice_user_client,
            method='post',
            data={'roles': ['a', 'b']},
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_cost_manager_cannot_add_a_role(self, authenticated_alice_user_client, user_alice, abc_user):
        user_alice.add_roles(roles.PAYMENT_MANAGER)
        assert not user_alice.is_full_admin
        assert user_alice.is_admin

        self.act(
            f'{self.detail_url(abc_user.id)}/admin',
            authenticated_alice_user_client,
            method='post',
            data={'roles': ['a', 'b']},
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_full_admin_can_add_roles(self, authenticated_alice_user_client, alice_full_admin, abc_user):
        abc_user.roles.clear()
        assert not abc_user.is_admin

        self.act(
            f'{self.detail_url(abc_user.id)}/admin',
            authenticated_alice_user_client,
            method='post',
            data={'roles': ['a', 'b']},
            status_code=status.HTTP_204_NO_CONTENT
        )

        abc_user.refresh_from_db()
        assert abc_user.is_admin
        assert abc_user.is_full_admin

    def test_full_admin_can_revoke_roles(self, authenticated_alice_user_client, alice_full_admin, abc_user):
        abc_user.add_roles(*[roles.FULL_ADMIN, roles.COTISATION_MANAGER, roles.COST_MANAGER])
        assert abc_user.is_admin
        assert abc_user.is_full_admin
        assert abc_user.is_cotisation_manager

        self.act(
            f'{self.detail_url(abc_user.id)}/admin',
            authenticated_alice_user_client,
            method='post',
            data={'roles': []},
            status_code=status.HTTP_204_NO_CONTENT
        )

        abc_user.refresh_from_db()
        assert not abc_user.is_admin
        assert not abc_user.is_full_admin
        assert not abc_user.is_cotisation_manager
