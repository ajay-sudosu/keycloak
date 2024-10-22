from keycloak import KeycloakAdmin

keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080",
    username="admin",
    password="admin",
    user_realm_name="master",
    realm_name="skylus",
)

realm_role_data = keycloak_admin.get_realm_role(
    role_name="d_adminstrator",
)

print(realm_role_data)
