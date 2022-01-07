from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status

from apps.profiles.models import User


class TestUserLoginView:
    login_url = reverse('profiles_urls:login_view')

    def test_init(self, user_alice):
        assert user_alice.email == 'alice@abc.com'
        assert user_alice.username == 'alice@abc.com'

    def test_unique_username_by_association(self, user_alice):
        try:
            User.objects.create_user(
                user_alice.username,
                email=user_alice.email,
                password='HelloWord4567',
                association=user_alice.association
            )
        except IntegrityError as exc:
            assert 'duplicate key value violates unique constraint "unique_username_by_association' in exc.args[0]

    def test_same_can_live_in_different_associations(self, user_alice, association_xyz):
        alice_xyz_user = User.objects.create_user(
            user_alice.username,
            email=user_alice.email,
            password='HelloWord4567',
            association=association_xyz
            )
        assert alice_xyz_user.email == user_alice.email
        assert alice_xyz_user.association != user_alice.association

    def test_cannot_login_without_a_valid_association(self, base_client, user_alice):
        response = base_client.post(self.login_url, {
            'email': user_alice.email,
            'password': 'Password123',
            'association': 'NON EXISTING'
        })
        response_data = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data['errors'][0]['detail'] == 'No active account found with the given credentials'

    def test_obtain_token(self, base_client, user_alice, association_abc):
        response = base_client.post(self.login_url, {
            'email': user_alice.email,
            'password': 'Password123',
            'association': association_abc.label.upper()
        })
        response_data = response.json()['data']
        assert response.status_code == status.HTTP_200_OK
        assert response_data['association'] == str(association_abc.id)
        assert 'access' in response_data
        assert 'refresh' in response_data
