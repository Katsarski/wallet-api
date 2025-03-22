import random
import uuid
import pytest
import requests

from AQA_Challenge import config


@pytest.fixture
def wallet_id():
    """Fixture to create a wallet ID for testing."""
    return str(uuid.uuid4())


@pytest.fixture
def funded_wallet(wallet_id, auth_headers):
    """Fixture to add an initial amount to the wallet and return the currency and amount added."""
    currency = random.choice(["USD", "EUR", "GBP"])
    amount = round(random.uniform(0.1, 500), 2)
    transaction_url = f"{config.BASE_URL}/wallet/{wallet_id}/transaction"
    payload = {"currency": currency, "amount": amount, "type": "credit"}
    response = requests.post(transaction_url, json=payload, headers=auth_headers)
    assert response.status_code == 200, "Failed to fund wallet"
    return {"wallet_id": wallet_id, "currency": currency, "amount": amount}