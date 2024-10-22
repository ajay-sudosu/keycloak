import requests
from keycloak import KeycloakOpenID

keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8080/",
    realm_name="master",
    client_id="user-login",
    client_secret_key="8a9qj3rXxVIphGFIehruPNvXWbHpZ0Vc",
)

# Obtain the token
token = keycloak_openid.token(
    username="admin",
    password="admin",
)

# Extract the access token
access_token = token['access_token']

# The API URL
URL = "http://localhost:8080/admin/realms/skylus/clients/547b5d29-0f65-4392-b143-59e0ac1d6246/authz/resource-server/policy/role/d15c6e96-894e-4980-aa95-d8f5c16ec164"

# Headers with correct Authorization field
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-type": "application/json",
}

# The payload to be sent
payload = {
    "id": "d15c6e96-894e-4980-aa95-d8f5c16ec164",
    "name": "server-read-1",
    "description": "",
    "type": "role",
    "logic": "POSITIVE",
    "decisionStrategy": "UNANIMOUS",
    "roles": [
        {
            "id": "341cad08-45f2-41e1-96f3-b869291b2cb2",
            "required": False
        },
        {
            "id": "44fafccd-0786-487b-8149-f4539f4c48cc",
            "required": False
        },
        {
            "id": "2547369d-6ee6-48e8-94c9-4074885bec00",
            "required": False
        },
        {
            "id": "f9c5785b-2529-456b-887d-00ba8ab3b66a",
            "required": False
        },
        {
            "id": "d803a92b-02ba-4956-995a-40519bb85d76",
            "required": False
        },
        {
            "id": "78b28371-0de5-46c4-be32-bcb6206f8083",
            "required": False
        },
        {
            "id": "78b28371-0de5-46c4-be32-bcb6206f8083",
            "required": False
        }
    ],
    "fetchRoles": True,
    "policies": []
}

# Sending the request
resp = requests.put(
    url=URL,
    headers=headers,
    json=payload,  # Pass the dictionary directly
)

# Print the response
print(resp.status_code)

print(resp.text)
