<h2>Wallet API Test Suite</h2>

## Overview

This test suite verifies the functionality of the POST /wallet/{walletId}/transaction endpoint in the Wallet API. It ensures transactions are processed correctly and validates expected behaviors under different conditions.

## Prerequisites

- Python 3.7+
- pip package manager

## Installation

- git clone <repository_url>
- cd <cloned_repo_dir>

**Create a virtual environment and install dependencies:**

    # Linux/MacOS
    - python3.# (tested and developed on 3.13) installed
    - run `apt install python3.13-venv` if not already there
    - run `python3 -m venv .venv`
    - run `source .venv/bin/activate`
    - run `pip install -r requirements.txt`

    # Windows
    - python3.# (tested and developed on 3.13) installed
    - run `python -m venv .venv`
    - run `.venv\Scripts\activate`  # On PowerShell or Command Prompt
    - run `pip install -r requirements.txt`
    - Optional (might be required): run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

##  Running tests

**Run all test cases using:**
- `pytest ./` - must be in project root dir

## Dependencies
- pytest
- requests
- pylint

**To install dependencies:**
- pip install pytest requests.txt

## Assumptions

- The authentication system is functional and returns a valid token
- Invalid payloads (e.g., negative amounts, unknown currencies) return 400 Bad Request


## Notes

### **Future Enhancements May Include:**
- Randomize the data even further (test with different currencies/amounts)
- Introduce environment-specific configurations that shall change based on the environment used
- Create a utility module to centralize API request logic, making it reusable and easier to maintain
- Use a separate module or files to store test data
- Add logging to log events such as which endopiunt is being called along with the outcomes 
- Implement linter checks for code quality
- Run tests in CI/CD pipeline
- Extend the coverage to cover the other endpoints further - ideally introduce E2E tests involving more endpoints in a certain scenario to cover complete user flows
- Introduce non-functional testing like performance and security
- Further check the source of data (DB) for data correctness + perform some tests there as well

### **Further Test Ideas:**
- Test wallet initialization with an invalid wallet ID
- Test transaction history retrieval
- Test endpoint timestamp properties are correctly added/updated
- Test transactions with different amounts (large amounts, very small amounts, currency combinations)
- Try to CRUD data using wallet/transaction IDs that belong to user X while using credentials of user Y
- Test the token encryption mechanism for security
- Test that regenerated tokens properly invalidate old tokens (old token cannot be reused)
- Test that expired tokens cannot be reused - correct error code returned (e.g., 401)
- Test how the transactions behave if the servive is put under load

## LLM used:
- Copilot GPT-4o (.gitignore, requirements.txt, generic README.md and TestPlan.txt structure)