"""
This module provides helper functions for interacting with the Wallet API.
It includes utilities for polling transaction statuses and ensuring transactions
are completed successfully.
"""

import time

import requests
import config


def wait_for_transaction_status_update(wallet_id, transaction_id, auth_headers, poll_interval = 1, 
                                       timeout=config.DEFAULT_API_TIMEOUT):
    """
    Polls the transaction status until it is no longer 'pending' or the timeout is reached.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(f"{config.BASE_URL}/{wallet_id}/transaction/{transaction_id}", 
                                headers=auth_headers,
                                timeout=config.DEFAULT_API_TIMEOUT)
        assert response.status_code == 200, "Failed to fetch transaction status"
        data = response.json()
        if data["status"] != "pending":
            return data
        time.sleep(poll_interval)  # Wait N seconds before retrying
    raise TimeoutError(f"Transaction {transaction_id} did not complete within {timeout} seconds")

def wait_for_transaction_succeeded(wallet_id, transaction_id, auth_headers, 
                                   timeout=config.DEFAULT_API_TIMEOUT):
    """
    Polls the transaction status until it is no longer 'pending' or the timeout is reached.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(f"{config.BASE_URL}/{wallet_id}/transaction/{transaction_id}", 
                                headers=auth_headers,
                                timeout=config.DEFAULT_API_TIMEOUT)
        assert response.status_code == 200, "Failed to fetch transaction status"
        data = response.json()
        if data["status"] == "finished" and data["outcome"] == "approved":
            return data
        time.sleep(1)  # Wait 1 seconds before retrying
    raise TimeoutError(f"Transaction {transaction_id} did not complete within "
                       f"{timeout} seconds")
