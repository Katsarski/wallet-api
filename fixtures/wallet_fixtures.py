"""This module provides fixtures for wallet related operations"""

import random
import uuid
import pytest
import requests
from common import helpers
import config

@pytest.fixture
def wallet_id():
    """Fixture to create a wallet ID for testing."""
    return str(uuid.uuid4())


@pytest.fixture
def funded_wallet(wallet_id, auth_headers):
    """Fixture to add an initial amount to the wallet and return the currency 
    and amount added."""
    transaction_url = f"{config.BASE_URL}/wallet/{wallet_id}/transaction"
    wallet_url = f"{config.BASE_URL}/wallet/{wallet_id}"

    # Fund the wallet with a random amount in X currency
    currency = random.choice(["USD", "EUR", "GBP"])
    amount = round(random.uniform(10, 500), 2)
    payload = {"currency": currency, "amount": amount, "type": "credit"}
    response = requests.post(transaction_url, 
                             json=payload, 
                             headers=auth_headers,
                             timeout=config.DEFAULT_API_TIMEOUT)

    assert response.status_code == 200, (
        f"Failed to fund wallet with {currency}, expected 200 but got {response.status_code}"
    )
    helpers.wait_for_transaction_succeeded(funded_wallet['wallet_id'], 
                                           response.json()["transactionId"], 
                                           auth_headers)

    # Verify the wallet waas funded
    wallet_response = requests.get(wallet_url, 
                                   headers=auth_headers,
                                   timeout=config.DEFAULT_API_TIMEOUT)
    
    assert wallet_response.status_code == 200, (
        f"Failed to fetch wallet data, expected 200 but got {wallet_response.status_code}"
    )
    wallet_data = wallet_response.json()
    assert len(wallet_data["currencyClips"]) == 1, "Wallet should have one currency clip"
    assert wallet_data["currencyClips"][0]["currency"] == currency, (
        f"Wallet currency is not {currency}"
    )
    assert wallet_data["currencyClips"][0]["amount"] == amount, (
        "Wallet amount does not match the funded amount"
    )

    return {"wallet_id": wallet_id, "currency": currency, "amount": amount}
