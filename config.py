import os

"""
This module provides configuration variables, for the time being they are not environment specific 
but can be further extended if needbe
"""

BASE_URL = "https://challenge.test.local/challenge/api/v1"
X_SERVICE_ID = os.getenv("X_SERVICE_ID")