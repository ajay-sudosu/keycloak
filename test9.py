import json
from keycloak import KeycloakAdmin

from helpers.keycloak_helpers_2 import format_realm_json

keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080",
    username="admin",
    password="admin",
    realm_name="master",
)

with open("data_2.json", "r", encoding="utf-8") as json_file:
    realm_data = json.load(json_file)


updated_json = format_realm_json(
    realm_json=realm_data,
    domain_name="test_my",
    office_365_custom=False,
)

# print(updated_json)


keycloak_admin.import_realm(
    payload=updated_json,
)
