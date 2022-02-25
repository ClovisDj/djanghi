from django.urls import reverse
from rest_framework import status

from apps.profiles import roles
from tests import ActMixin


class TestMembershipPaymentsViewSet(ActMixin):

    @staticmethod
    def get_list_url(user):
        return reverse('membership-payments-list', kwargs={'user_pk': str(user.id)})

    @staticmethod
    def detail_url(uu_id):
        return reverse('users-detail', args=(str(uu_id), ))

    def test_an_unauthenticated_user_cannot_list_any_membership_payment(self, base_client, abc_user, user_alice):
        self.act(self.get_list_url(abc_user), base_client, method='get', status_code=status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_regular_user_cannot_add_a_membership_payment(self, authenticated_abc_user_client, abc_user):
        self.act(
            self.get_list_url(abc_user),
            authenticated_abc_user_client, data={'amount': 10.5},
            method='post',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_authenticated_full_admin_can_add_a_user_membership_payment(self, authenticated_abc_user_client, abc_user,
                                                                        user_alice, abc_payments_type):
        abc_user.add_roles(roles.FULL_ADMIN)

        self.act(
            self.get_list_url(user_alice),
            authenticated_abc_user_client, data={
                'amount': 10.5,
                'membership_payment_type_id': str(abc_payments_type[0].id)
            },
            method='post',
            status_code=status.HTTP_201_CREATED
        ).json()
