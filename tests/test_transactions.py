"""This module provides tests for wallet transactions."""

import random
import requests
import config
from common import helpers

def test_wallet_initialization_and_initial_transactions(wallet_id, auth_headers):
    """Test wallet initialization and multiple currency transactions."""
    # Generate a wallet ID and verify it is initially empty
    wallet_url = f"{config.BASE_URL}/wallet/{wallet_id}"
    response = requests.get(wallet_url, 
                            headers=auth_headers, 
                            timeout=config.DEFAULT_API_TIMEOUT)
    
    assert response.status_code == 200, (
        f"Wallet initialization failed, expected 200 but got {response.status_code}"
    )

    data = response.json()
    assert data["currencyClips"] == []
    
    transaction_url = f"{config.BASE_URL}/wallet/{wallet_id}/transaction"
    currencies = ["USD", "EUR", "GBP"]
    transaction_ids = []
    transaction_data = []

    # Perform credit transaction for each avaialble currency
    for currency in currencies:
        payload = {"currency": currency, 
                   "amount": round(random.uniform(1, 500), 2), 
                   "type": "credit"}        
        
        response = requests.post(transaction_url, 
                                 json=payload, 
                                 headers=auth_headers, 
                                 timeout=config.DEFAULT_API_TIMEOUT)
        
        assert response.status_code == 200, (
            f"Failed to perform transaction for {currency} expected 200 but "
            f"got {response.status_code}"
        )
        data = response.json()
        assert "transactionId" in data, "Transaction ID not found in response"
        assert data["status"] in ["pending", "finished"], (
            f'Transaction status is not pending or finished but {data["status"]}'
        )
        
        transaction_ids.append(data["transactionId"])
        transaction_data.append({"currency": currency, "amount": payload["amount"]})

    # assert all transactions are finished and approved
    assert len(transaction_ids) == len(currencies), (
        "Amount of transactions does not match amount of currencies"
    )

    for transaction_id in transaction_ids:
        helpers.wait_for_transaction_status_update(wallet_id, 
                                                   transaction_id, 
                                                   auth_headers)
        
        response = requests.get(f"{transaction_url}/{transaction_id}", 
                                headers=auth_headers, 
                                timeout=config.DEFAULT_API_TIMEOUT)
        
        assert response.status_code == 200, (
            f"Failed to fetch transaction {transaction_id}, expected 200 but "
            "got {response.status_code}"
        )

        data = response.json()
        assert data["status"] == "finished", f"Transaction {transaction_id} did not finish"
        assert data["outcome"] == "approved", f"Transaction {transaction_id} was not approved"
    
    # Fetch wallet data and verify that the transactions were successfully reflected there
    response = requests.get(wallet_url, 
                            headers=auth_headers, 
                            timeout=config.DEFAULT_API_TIMEOUT)
    
    assert response.status_code == 200, (
        f"Failed to fetch wallet data, expected 200 but got {response.status_code}"
    )
    data = response.json()
    assert len(data["currencyClips"]) == len(currencies), (
        "Amount of currencies in wallet does not match amount of transactions made"
    )

    # assert that for each wallet currency clip we have the respective currency 
    # and amount from the transactions made
    for currency_clip in data["currencyClips"]:
        assert currency_clip["currency"] in currencies, (
            f"Currency {currency_clip['currency']} not found in transactions"
        )
        for transaction in transaction_data:
            if transaction["currency"] == currency_clip["currency"]:
                assert currency_clip["amount"] == transaction["amount"], (
                    f"Amount of currency {currency_clip['currency']} does not match "
                    "transaction amount"
                )
    
def test_credit_transaction_exceeding_bank_balance(wallet_id, auth_headers):
    """Test that exceeding the balance of the bank/3rd party service making 
    the payment causes the transaction to be denied"""
    # Test assumes that the bank/3rd party service account starts with a balance 
    # of 100 USD, should be configured in that way
    bank_available_amount = 100
    transaction_url = f"{config.BASE_URL}/wallet/{wallet_id}/transaction"

    # Perform the first transaction within the balance
    first_transaction_payload = {"currency": "USD", 
                                 "amount": bank_available_amount, 
                                 "type": "credit"}
    
    first_transaction_response = requests.post(transaction_url, 
                                               json=first_transaction_payload, 
                                               headers=auth_headers, 
                                               timeout=config.DEFAULT_API_TIMEOUT)

    # Perform the second transaction exceeding the balance immediately
    second_transaction_payload = {"currency": "USD", "amount": 1, "type": "credit"}
    second_transaction_response = requests.post(transaction_url, 
                                                json=second_transaction_payload, 
                                                headers=auth_headers, 
                                                timeout=config.DEFAULT_API_TIMEOUT)

    first_transaction_id = first_transaction_response.json()["transactionId"]
    second_transaction_id = second_transaction_response.json()["transactionId"]

    # Wait for both transactions to complete
    first_transaction_data = helpers.wait_for_transaction_status_update(wallet_id, 
                                                                        first_transaction_id, 
                                                                        auth_headers)
    second_transaction_data = helpers.wait_for_transaction_status_update(wallet_id, 
                                                                         second_transaction_id, 
                                                                         auth_headers)

    # Assert the first transaction was performed successfuly and the second was denied
    
    assert first_transaction_data["status"] == "finished", (
        "First transaction did not finish"
    )
    assert first_transaction_data["outcome"] == "approved", (
        "First transaction was not approved"
    )

    assert second_transaction_data["status"] == "finished", (
        "Second transaction did not finish"
    )
    assert second_transaction_data["outcome"] == "denied", (
        "Second transaction was not denied as expected"
    )

def test_debit_transaction_exceeding_wallet_balance(funded_wallet, auth_headers):
    """Test that exceeding the balance of the wallet causes the debit transaction 
    to be denied"""
    # Add some initial funds to the wallet and wait for the transaction to finish
    transaction_url = f"{config.BASE_URL}/wallet/{funded_wallet['wallet_id']}/transaction"

    # Perform the first transaction within the balance
    first_transaction_payload = {"currency": funded_wallet["currency"], 
                                 "amount": funded_wallet["amount"], "type": "debit"}
    first_transaction_response = requests.post(transaction_url, 
                                               json=first_transaction_payload, 
                                               headers=auth_headers, 
                                               timeout=config.DEFAULT_API_TIMEOUT)

    # Immediately Perform the second transaction which is exceeding the balance
    second_transaction_payload = {"currency": funded_wallet["currency"], 
                                  "amount": 1, "type": "debit"}
    second_transaction_response = requests.post(transaction_url, 
                                                json=second_transaction_payload, 
                                                headers=auth_headers, 
                                                timeout=config.DEFAULT_API_TIMEOUT)

    first_transaction_id = first_transaction_response.json()["transactionId"]
    second_transaction_id = second_transaction_response.json()["transactionId"]

    # Wait for both transactions to complete
    first_transaction_data = helpers.wait_for_transaction_status_update(
        funded_wallet["wallet_id"],
        first_transaction_id, auth_headers)
    second_transaction_data = helpers.wait_for_transaction_status_update(
        funded_wallet["wallet_id"], 
        second_transaction_id, auth_headers)

    # Assert the first transaction was performed successfuly and the second was denied
    assert first_transaction_data["status"] == "finished", (
        "First transaction did not finish"
    )
    assert first_transaction_data["outcome"] == "approved", (
        "First transaction was not approved"
    )

    assert second_transaction_data["status"] == "finished", (
        "Second transaction did not finish"
    )
    assert second_transaction_data["outcome"] == "denied", (
        "Second transaction was not denied as expected"
    )

def test_concurrent_transactions(wallet_id, auth_headers):
    """
    Test performing multiple transactions sequentially and verify that they are
      processed correctly.
    """
    transaction_amount = round(random.uniform(1, 500), 2)

    transaction_url = f"{config.BASE_URL}/wallet/{wallet_id}/transaction"
    payloads = [
        {"currency": "USD", "amount": transaction_amount, "type": "credit"},
        {"currency": "USD", "amount": transaction_amount, "type": "credit"},
        {"currency": "USD", "amount": transaction_amount, "type": "debit"},
        {"currency": "USD", "amount": transaction_amount, "type": "credit"},
        {"currency": "USD", "amount": transaction_amount, "type": "debit"}
    ]

    responses = [requests.post(transaction_url, 
                               json=payload, headers=auth_headers, 
                               timeout=config.DEFAULT_API_TIMEOUT) 
                               for payload in payloads]
    
    transaction_ids = [response.json()["transactionId"] for response in responses]

    for transaction_id in transaction_ids:
        transaction_data = helpers.wait_for_transaction_succeeded(wallet_id, 
                                                                  transaction_id, 
                                                                  auth_headers)
        assert transaction_data["status"] == "finished", (
            f"Transaction {transaction_id} did not finish"
        )

    # Fetch wallet data and verify that the transactions were successfully reflected there
    response = requests.get(f"{config.BASE_URL}/wallet/{wallet_id}", 
                            headers=auth_headers, 
                            timeout=config.DEFAULT_API_TIMEOUT)
    
    assert response.status_code == 200, (
        f"Failed to fetch wallet data, expected 200 but got {response.status_code}"
    )
    data = response.json()
    assert len(data["currencyClips"]) == 1, (
        "Available wallet currencies does not match the amount of transactions made"
    )
    assert data["currencyClips"][0]["amount"] == transaction_amount, (
        "Amount of currency in wallet does not match transaction amount"
    )

def test_large_volume_of_transactions(wallet_id, auth_headers):
    """
    Test the system's ability to handle a large number of transactions in a short period.
    """
    # Test assumes there are sufficient funds in the bank/3rd party service account 
    # to perform the transactions
    transaction_url = f"{config.BASE_URL}/wallet/{wallet_id}/transaction"
    num_transactions = 100
    transaction_ids = []

    # Perform 100 credit transactions
    for _ in range(num_transactions):
        payload = {"currency": "USD", 
                   "amount": round(random.uniform(1, 10), 2), 
                   "type": "credit"}
        
        response = requests.post(transaction_url, 
                                 json=payload, 
                                 headers=auth_headers, 
                                 timeout=config.DEFAULT_API_TIMEOUT)
        
        assert response.status_code == 200, "Failed to perform transaction"
        transaction_ids.append(response.json()["transactionId"])

    # Verify all transactions are processed
    for transaction_id in transaction_ids:
        transaction_data = helpers.wait_for_transaction_status_update(wallet_id, 
                                                                      transaction_id, 
                                                                      auth_headers)
        assert transaction_data["status"] == "finished", (
            f"Transaction {transaction_id} did not finish"
        )
        assert transaction_data["outcome"] == "approved", (
            f"Transaction {transaction_id} was not approved"
        )

def test_transaction_invalid_payload(wallet_id, auth_headers):
    """
    Test that invalid payloads are rejected by the API. (ideally separate tests for 
    each case for more fine-tuned assertions)
    """
    transaction_url = f"{config.BASE_URL}/wallet/{wallet_id}/transaction"

    # Add initial funds to the wallet
    transaction_amount = round(random.uniform(100, 500), 2)
    credit_payload = {"currency": "USD", "amount": transaction_amount, "type": "credit"}
    credit_response = requests.post(transaction_url, 
                                    json=credit_payload, 
                                    headers=auth_headers, 
                                    timeout=config.DEFAULT_API_TIMEOUT)
    
    helpers.wait_for_transaction_succeeded(wallet_id, 
                                           credit_response.json()["transactionId"], 
                                           auth_headers)

    # Test assumes a 400 response is returned when an invalid parameter is used
    payloads = [
        {"currency": "USD", "amount": -1, "type": "credit"},  # Negative amount
        {"currency": "USD", "amount": 1, "type": "invalid"},  # Invalid transaction type
        {"currency": "invalid", "amount": 1, "type": "credit"},  # Invalid currency
        {"currency": "USD", "amount": 1, "type": "credit", 
         "invalid_key": "invalid_value"},  # Extra key in payload
        {"amount": 1, "type": "credit"},  # Missing currency
        {"currency": "USD", "type": "credit"},  # Missing amount
        {"currency": "USD", "amount": 1},  # Missing type
        {"currency": "USD", "amount": 0, "type": "credit"}, # Zero amount
    ]
    for payload in payloads:
        response = requests.post(transaction_url, 
                                 json=payload, 
                                 headers=auth_headers, 
                                 timeout=config.DEFAULT_API_TIMEOUT)
        
        assert response.status_code == 400, f"Expected 400 but got {response.status_code}"

    # Verify wallet balance remains unchanged
    wallet_url = f"{config.BASE_URL}/wallet/{wallet_id}"
    wallet_response = requests.get(wallet_url, 
                                   headers=auth_headers, 
                                   timeout=config.DEFAULT_API_TIMEOUT)
    
    assert wallet_response.status_code == 200, "Failed to fetch wallet data"
    wallet_data = wallet_response.json()
    assert wallet_data["currencyClips"][0]["amount"] == transaction_amount, (
        "Wallet balance changed after failed transaction"
    )

def test_transaction_timeout(wallet_id, auth_headers):
    """
    Test that a transaction in the 'pending' state is automatically denied after 30 minutes.
    """
    transaction_url = f"{config.BASE_URL}/wallet/{wallet_id}/transaction"

    # Initiate a transaction that will remain in the 'pending' state
    payload = {"currency": "USD", "amount": 100, "type": "credit"}
    response = requests.post(transaction_url, 
                             json=payload, 
                             headers=auth_headers, 
                             timeout=config.DEFAULT_API_TIMEOUT)
    
    assert response.status_code == 200, "Failed to initiate transaction"
    transaction_data = response.json()

    # Verify the initial status is 'pending'
    assert transaction_data["status"] == "pending", "Transaction did not start in 'pending' state"

    # Simulate a transaction timeout on the remote server end and query in some interval till 
    # 30 minutes have passed

    # Fetch the transaction status after the timeout
    timeout_response = helpers.wait_for_transaction_status_update(wallet_id, 
                                                                  transaction_data["transactionId"], 
                                                                  auth_headers, 
                                                                  timeout=1800)
    assert timeout_response["status"] == "finished", (
        "Transaction did not move to 'finished' state after timeout"
    )
    assert timeout_response["outcome"] == "denied", "Transaction was not denied after timeout"

    # Verify the wallet balance remains unchanged
    wallet_url = f"{config.BASE_URL}/wallet/{wallet_id}"
    wallet_response = requests.get(wallet_url, 
                                   headers=auth_headers, 
                                   timeout=config.DEFAULT_API_TIMEOUT)
    
    assert wallet_response.status_code == 200, "Failed to fetch wallet data"
    wallet_data = wallet_response.json()
    assert len(wallet_data["currencyClips"]) == 0, (
        "Wallet balance should remain unchanged after denied transaction"
    )
    
    