from keycloak import KeycloakAdmin


keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080",
    username="admin",
    password="admin",
    realm_name="skylus",
    user_realm_name="master",
)

group_data = keycloak_admin.get_group_by_path(
    path="projects/test-project-1",
)

keycloak_admin.update_group(
    group_id=group_data["id"],
    payload={
        "name": "test-project-1",
        "attributes": {"pa": ["askfnaslkfnalfnal"]}
    },
)
