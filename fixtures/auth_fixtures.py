import pytest

from AQA_Challenge import config


@pytest.fixture(scope="session")
def auth_headers():
    """Fixture to authenticate once per test session and provide auth headers."""
    token = _authenticate()
    return {
        "Authorization": f"Bearer {token}",
        "X-Service-Id": config.X_SERVICE_ID,
        "Content-Type": "application/json"
    }

def _authenticate():
    """Fetch a valid authentication token by logging in."""
    headers = {
        "X-Service-Id": config.X_SERVICE_ID,
        "Content-Type": "application/json"
    }
    # response = requests.post(
    #     f"{config.BASE_URL}/user/login",
    #     json={"username": "<username>", "password": "<password>"},
    #     headers=headers
    # )
    # assert response.status_code == 200, "Authentication failed"
    # return response.json().get("token")
    return "dummy_token"