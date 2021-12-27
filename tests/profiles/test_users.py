from django.urls import reverse
from rest_framework import status

from tests import ActMixin


class TestUserModelViewSet(ActMixin):
    list_url = reverse('profiles_urls:users-list')
    # detail_url = reverse('profiles_urls:users-detail', args=(<uuid>, ))

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
