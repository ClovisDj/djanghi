from django.urls import reverse
from rest_framework import status

from tests import ActMixin


class TestUserRegistrationLink(ActMixin):
    list_url = reverse('profiles_urls:registrations-list')

    @staticmethod
    def detail_url(uu_id):
        return reverse('profiles_urls:registration-detail', args=(str(uu_id), ))

    @property
    def create_data(self):
        return {
            'email': 'johny@mebam.com',
            'first_name': 'John',
        }

    def test_regular_user_cannot_send_a_registration_link(self, authenticated_alice_user_client):
        self.act(self.list_url, authenticated_alice_user_client, data=self.create_data,
                 status_code=status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_list_a_registration_link(self, authenticated_abc_user_client,
                                                          inactive_abc_user_registration_link):
        self.act(self.list_url, authenticated_abc_user_client, method='get',
                 status_code=status.HTTP_403_FORBIDDEN)

    def test_full_admin_can_generate_a_registration_link(self, authenticated_alice_user_client, alice_full_admin):
        response = self.act(self.list_url, authenticated_alice_user_client, data=self.create_data,
                            status_code=status.HTTP_201_CREATED).json()

        attributes = response['data']['attributes']
        user_id = response['data']['relationships']['user']['data']['id']
        created_user_attributes = {}
        for user in response['included']:
            if user['id'] == user_id:
                created_user_attributes = user['attributes']

        assert 'link' in attributes
        assert attributes['is_active']
        assert not created_user_attributes['is_active']
        assert not created_user_attributes['is_registered']
        assert created_user_attributes['email'] == self.create_data['email']
        assert created_user_attributes['first_name'] == self.create_data['first_name']

