import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Define the scopes and token file path
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_PATH = "emailservice/kytoken.json"

def validate_token():
    """Validate the Gmail API token from token.json."""
    if not os.path.exists(TOKEN_PATH):
        print("Token file not found.")
        return False

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    creds.refresh(Request())
    print(creds.refresh_token)
    if creds and creds.valid:
        print("Token is valid.")
        return True
    elif creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            print("Token refreshed successfully.")
            return True
        except Exception as e:
            print("Token refresh failed:", e)
            return False
    else:
        print("Token is not valid.")
        return False

if __name__ == "__main__":
    is_valid = validate_token()
    print("Is token valid?", is_valid)
