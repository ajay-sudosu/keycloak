import json
import requests
from keycloak import KeycloakAdmin, KeycloakOpenID

keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080",
    username="admin",
    password="admin",
    realm_name="skylus",
    user_realm_name="master",
)

keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8080",
    realm_name="master",
    client_id="user-login",
    client_secret_key="8a9qj3rXxVIphGFIehruPNvXWbHpZ0Vc",
)

client_uuid = keycloak_admin.get_client_id(
    client_id="compute-service",
)

access_token = keycloak_openid.token(
    username="admin",
    password="admin",
)


URL = f"http://localhost:8080/admin/realms/skylus/clients/{client_uuid}/authz/resource-server/policy/search"

query_param = {
    "name": "server-read-1",
}

headers = {
    "Authorization": f"Bearer {access_token['access_token']}",
    "Content-type": "application/json",
}

resp = requests.get(
    url=URL,
    params=query_param,
    headers=headers,
)

item = resp.json()

print(item)

print(type(json.loads(item['config']['roles'])))

keycloak_openid.logout(
    refresh_token=access_token["refresh_token"],
)

