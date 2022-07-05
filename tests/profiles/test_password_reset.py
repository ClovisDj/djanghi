from django.core import mail
from django.urls import reverse
from rest_framework import status

from tests import ActMixin


class TestPasswordResetLink(ActMixin):
    list_url = reverse('profiles_urls:reset-password-list')

    def test_cannot_list_password_reset_endpoint(self, authenticated_alice_user_client, alice_full_admin,
                                                 association_abc):
        self.act(self.list_url,
                 authenticated_alice_user_client,
                 method='get',
                 status_code=status.HTTP_403_FORBIDDEN)

    def test_a_user_from_an_inactive_association_cannot_reset_his_password(self, base_client, user_alice,
                                                                           association_abc):
        association_abc.is_active = False
        association_abc.save()

        assert user_alice.is_active

        self.act(self.list_url,
                 base_client,
                 data={'email': user_alice.email, 'association_label': association_abc.label},
                 status_code=status.HTTP_401_UNAUTHORIZED)

    def test_an_inactive_user_from_an_active_association_cannot_reset_his_password(self, base_client, user_alice,
                                                                                   association_abc):
        user_alice.is_active = False
        user_alice.save()

        assert association_abc.is_active

        self.act(self.list_url,
                 base_client,
                 data={'email': user_alice.email, 'association_label': association_abc.label},
                 status_code=status.HTTP_401_UNAUTHORIZED)

    def test_a_user_cannot_reset_the_password_of_a_user_in_another_association(self, base_client, user_alice,
                                                                               association_abc, association_xyz):
        assert association_xyz.is_active
        assert user_alice.is_active

        self.act(self.list_url,
                 base_client,
                 data={'email': user_alice.email, 'association_label': association_xyz.label},
                 status_code=status.HTTP_401_UNAUTHORIZED)

    def test_a_user_with_proper_credentials_can_reset_his_password(self, base_client, user_alice, association_abc):
        assert association_abc.is_active
        assert user_alice.is_active

        self.act(self.list_url,
                 base_client,
                 data={
                     'email': user_alice.username,
                     'association_label': association_abc.label
                 },
                 status_code=status.HTTP_201_CREATED)

    def test_reset_password_params_should_be_case_insensitive(self, base_client, user_alice, association_abc):
        assert not user_alice.password_resets.exists()

        self.act(self.list_url,
                 base_client,
                 data={
                     'email': user_alice.username.upper(),
                     'association_label': association_abc.label.upper()
                 },
                 status_code=status.HTTP_201_CREATED)

        assert user_alice.password_resets.count() == 1

    def test_reset_password_endpoint_should_send_reset_email(self, base_client, user_alice, association_abc):
        assert len(mail.outbox) == 0

        self.act(self.list_url,
                 base_client,
                 data={
                     'email': user_alice.username.upper(),
                     'association_label': association_abc.label.title()
                 },
                 status_code=status.HTTP_201_CREATED)

        assert len(mail.outbox) == 1

