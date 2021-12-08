

def test_test_init(user_alice):
    assert user_alice.email == 'alice@abc.com'
    assert user_alice.username == 'alice@abc.com'
