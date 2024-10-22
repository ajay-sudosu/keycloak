import requests
import json

from keycloak import KeycloakOpenID


# keycloak_admin = KeycloakAdmin(
#     server_url="http://localhost:8080",
#     username="admin",
#     password="admin",
#     user_realm_name="master",
#     realm_name="skylus",
# )

# payload = keycloak_admin.get_client_authz_policy(
#     client_id="547b5d29-0f65-4392-b143-59e0ac1d6246",
#     policy_id="d15c6e96-894e-4980-aa95-d8f5c16ec164",
# )

# print(payload)

keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8080/",
    realm_name="skylus",
    client_id="user-login",
    client_secret_key="cbN5KnwmGKMNxPaNkNvNdHUUXX6aNNgn",
)

token=keycloak_openid.token(
    username="jaswanth",
    password="netweb2",
)

URL = "http://localhost:8080/admin/realms/skylus/clients/547b5d29-0f65-4392-b143-59e0ac1d6246/authz/resource-server/policy/role/d15c6e96-894e-4980-aa95-d8f5c16ec164"

headers = {
    "Authentication": f"Bearer {token['access_token']}",
    "Content-type": "application/json",
}

payload = {
    "id": "d15c6e96-894e-4980-aa95-d8f5c16ec164",
    "name": "server-read-1",
    "description": "",
    "type": "role",
    "logic": "POSITIVE",
    "decisionStrategy": "UNANIMOUS",
    "roles": [],
    "fetchRoles": True,
    "policies": [],
}

resp = requests.request(
    "PUT",
    headers=headers,
    url=URL,
    json=json.dumps(payload),
)

print(resp.json())
