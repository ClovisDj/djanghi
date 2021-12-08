from django.urls import reverse


class TestLoginView:
    def test_init(self, user_alice):
        assert user_alice.email == 'alice@abc.com'
        assert user_alice.username == 'alice@abc.com'
