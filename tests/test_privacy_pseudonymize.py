from app.privacy.pseudonymize import pseudonymize


def test_same_input_gives_same_token():
    a = pseudonymize("employee-123", secret="s3cret")
    b = pseudonymize("employee-123", secret="s3cret")
    assert a == b


def test_different_employees_give_different_tokens():
    a = pseudonymize("employee-123", secret="s3cret")
    b = pseudonymize("employee-456", secret="s3cret")
    assert a != b


def test_different_secret_gives_different_token():
    # Same employee, different tenant secret -> unlinkable across tenants.
    a = pseudonymize("employee-123", secret="s3cret")
    b = pseudonymize("employee-123", secret="a-different-secret")
    assert a != b


def test_token_does_not_contain_the_original_identifier():
    token = pseudonymize("employee-123", secret="s3cret")
    assert "employee-123" not in token
    assert "123" not in token


def test_token_has_expected_shape():
    token = pseudonymize("employee-123", secret="s3cret", prefix="EMP")
    assert token.startswith("EMP-")
    assert len(token) == len("EMP-") + 10
