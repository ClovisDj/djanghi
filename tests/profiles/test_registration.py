import datetime
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from tests import ActMixin


class TestUserRegistrationLink(ActMixin):
    list_url = reverse('profiles_urls:registrations-list')

    @staticmethod
    def detail_url(uu_id):
        return reverse('profiles_urls:registrations-detail', args=(str(uu_id), ))

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

    def test_cannot_send_registration_link_for_already_registered_user(self, authenticated_alice_user_client,
                                                                       alice_full_admin, abc_user):
        response = self.act(self.list_url, authenticated_alice_user_client, data={'email': abc_user.email},
                            status_code=status.HTTP_400_BAD_REQUEST).json()

        assert response['errors'][0]['detail'] == 'This user is already registered'

    def test_admin_can_only_list_his_association_registration_links(self, authenticated_alice_user_client,
                                                                    alice_full_admin,
                                                                    inactive_abc_user_registration_link,
                                                                    inactive_xyz_user_registration_link):

        response = self.act(self.list_url, authenticated_alice_user_client, method='get',
                            status_code=status.HTTP_200_OK).json()
        assert response['meta']['pagination']['count'] == 1
        assert response['data'][0]['id'] == str(inactive_abc_user_registration_link.id)

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

    def test_can_resend_an_expired_registration_link(self, authenticated_alice_user_client, alice_full_admin,
                                                     inactive_abc_user_registration_link):
        detail_url = self.detail_url(inactive_abc_user_registration_link.id)
        previous_expiration_date = timezone.now() - datetime.timedelta(days=1)
        inactive_abc_user_registration_link.expiration_date = previous_expiration_date
        inactive_abc_user_registration_link.save()

        assert not inactive_abc_user_registration_link.is_active()

        response = self.act(detail_url, authenticated_alice_user_client, data={}, method='patch',
                            status_code=status.HTTP_200_OK).json()

        attributes = response['data']['attributes']
        inactive_abc_user_registration_link.refresh_from_db()
        assert attributes['is_active']
        assert inactive_abc_user_registration_link.is_active()


