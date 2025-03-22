
"""
This module provides configuration variables, for the time being they are not environment specific 
but can be further extended if needbe
"""

import os

BASE_URL = "https://challenge.test.local/challenge/api/v1"
X_SERVICE_ID = os.getenv("X_SERVICE_ID")
DEFAULT_API_TIMEOUT = 30
