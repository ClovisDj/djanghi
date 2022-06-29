import copy
import datetime
from django.core import mail
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.profiles import roles
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
        assert created_user_attributes['is_active']
        assert not created_user_attributes['is_registered']
        assert created_user_attributes['email'] == self.create_data['email']
        assert created_user_attributes['first_name'] == self.create_data['first_name']

    def test_can_resend_an_expired_registration_link(self, authenticated_alice_user_client, alice_full_admin,
                                                     inactive_abc_user_registration_link):
        detail_url = self.detail_url(inactive_abc_user_registration_link.id)
        previous_expiration_date = timezone.now() - datetime.timedelta(days=1)
        inactive_abc_user_registration_link.expiration_date = previous_expiration_date
        inactive_abc_user_registration_link.save()

        assert not inactive_abc_user_registration_link.is_active

        response = self.act(detail_url, authenticated_alice_user_client, data={}, method='patch',
                            status_code=status.HTTP_200_OK).json()

        attributes = response['data']['attributes']
        inactive_abc_user_registration_link.refresh_from_db()
        assert attributes['is_active']
        assert inactive_abc_user_registration_link.is_active

    def test_a_payments_manager_cannot_send_a_user_registration_link_email_without_correct_params(
            self, authenticated_alice_user_client, user_alice):

        user_alice.add_roles(roles.PAYMENT_MANAGER)
        user_alice.refresh_from_db()
        assert user_alice.is_payment_manager
        create_data = copy.deepcopy(self.create_data)
        create_data['should_send_activation'] = False

        self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=create_data,
            status_code=status.HTTP_201_CREATED
        )

        assert len(mail.outbox) == 0

    def test_a_payments_manager_can_send_a_user_registration_link_email(self, authenticated_alice_user_client,
                                                                        user_alice):
        user_alice.add_roles(roles.PAYMENT_MANAGER)
        user_alice.refresh_from_db()
        assert user_alice.is_payment_manager
        create_data = copy.deepcopy(self.create_data)
        create_data['should_send_activation'] = True

        self.act(
            self.list_url,
            authenticated_alice_user_client,
            data=create_data,
            status_code=status.HTTP_201_CREATED
        )

        assert len(mail.outbox) == 1
        out_email = mail.outbox[0]
        assert len(out_email.to) == 1
        assert out_email.to[0] == create_data['email']
        assert out_email.from_email == settings.DEFAULT_FROM_EMAIL
        assert len(out_email.alternatives) == 1


class TestUserRegistrationPage:
    url = '/activate/{association_id}/{user_id}/{link_id}'
    client = Client()

    @property
    def registration_data(self):
        return {
            'first_name': 'Emily',
            'last_name': 'Djometsa',
            'password': '123Password',
            'password_verification': '123Password',
        }

    def test_cannot_retrieve_an_expired_link_page(self, expired_abc_user_registration_link):
        response = self.client.get(
            self.url.format(
                association_id=str(expired_abc_user_registration_link.association_id),
                user_id=str(expired_abc_user_registration_link.user_id),
                link_id=str(expired_abc_user_registration_link.id),
            )
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_retrieve_a_deactivated_link_page(self, inactive_abc_user_registration_link):
        inactive_abc_user_registration_link.is_deactivated = True
        inactive_abc_user_registration_link.save()

        response = self.client.get(
            self.url.format(
                association_id=str(inactive_abc_user_registration_link.association_id),
                user_id=str(inactive_abc_user_registration_link.user_id),
                link_id=str(inactive_abc_user_registration_link.id),
            )
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_retrieve_malformed_link_page(self, inactive_abc_user_registration_link, association_xyz):
        inactive_abc_user_registration_link.is_deactivated = True
        inactive_abc_user_registration_link.save()

        response = self.client.get(
            self.url.format(
                association_id=str(association_xyz.id),
                user_id=str(inactive_abc_user_registration_link.user_id),
                link_id=str(inactive_abc_user_registration_link.id),
            )
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_cannot_register_from_an_invalid_registration_link(self, inactive_abc_user_registration_link):
        inactive_abc_user_registration_link.is_deactivated = True
        inactive_abc_user_registration_link.save()

        response = self.client.post(
            self.url.format(
                association_id=str(inactive_abc_user_registration_link.association_id),
                user_id=str(inactive_abc_user_registration_link.user_id),
                link_id=str(inactive_abc_user_registration_link.id),
            ),
            data=self.registration_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_can_open_a_valid_link_page(self, inactive_abc_user_registration_link):
        response = self.client.get(
            self.url.format(
                association_id=str(inactive_abc_user_registration_link.association_id),
                user_id=str(inactive_abc_user_registration_link.user_id),
                link_id=str(inactive_abc_user_registration_link.id),
            )
        )
        assert response.status_code == status.HTTP_200_OK

    def test_user_can_properly_register_with_valid_registration_link(self, inactive_abc_user_registration_link):
        response = self.client.post(
            self.url.format(
                association_id=str(inactive_abc_user_registration_link.association_id),
                user_id=str(inactive_abc_user_registration_link.user_id),
                link_id=str(inactive_abc_user_registration_link.id),
            ),
            data=self.registration_data
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert 'refresh=' in response.url
        assert 'access=' in response.url

        user = inactive_abc_user_registration_link.user
        user.refresh_from_db()
        assert user.is_active
        assert user.is_registered
