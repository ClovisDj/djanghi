from django.urls import reverse
from rest_framework import status


class TestLoginView:
    login_url = reverse('profiles_urls:login_view')

    def test_init(self, user_alice):
        assert user_alice.email == 'alice@abc.com'
        assert user_alice.username == 'alice@abc.com'

    def test_cannot_login_without_a_valid_association(self, base_client, user_alice):
        response = base_client.post(self.login_url, {
            'email': user_alice.email,
            'password': 'Password123',
            'association': 'NON EXISTING'
        })
        response_data = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data['detail'] == 'No active account found with the given credentials'

    def test_obtain_token(self, base_client, user_alice, association_abc):
        response = base_client.post(self.login_url, {
            'email': user_alice.email,
            'password': 'Password123',
            'association': association_abc.label.upper()
        })
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data['association'] == str(association_abc.id)
        assert 'access' in response_data
        assert 'refresh' in response_data
