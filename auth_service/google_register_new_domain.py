import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Path to your service account key file
SERVICE_ACCOUNT_FILE = '/home/ajay-netweb/PycharmProjects/keycloak/key/my_key.json'

# Client ID for which you're updating the redirect URIs
CLIENT_ID = '167968602924-tghvbplk6ojo7it6f2lqqegnmr24sono.apps.googleusercontent.com'

# Google API endpoint to update the client
UPDATE_URL = f'https://oauth2.googleapis.com/v1/clients/{CLIENT_ID}'

# List of new redirect URIs
redirect_uris = [
    "http://localhost:8080/realms/jasu/broker/google/endpoint"]


# Authenticate with service account credentials
def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    request = Request()
    credentials.refresh(request)
    access_token = credentials.token
    credentials.refresh(request)

    return access_token


def update_redirect_uris():
    access_token = get_access_token()

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    data = {
        "redirect_uris": redirect_uris
    }

    response = requests.patch(UPDATE_URL, headers=headers, json=data)

    if response.status_code == 200:
        print("Redirect URIs updated successfully!")
    else:
        print(f"Failed to update redirect URIs. Status code: {response.status_code}")
        print(f"Response: {response.text}")


if __name__ == "__main__":
    update_redirect_uris()
