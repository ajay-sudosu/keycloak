from keycloak import KeycloakAdmin

keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080",
    username="admin",
    password="admin",
    user_realm_name="master",
    realm_name="skylus",
)

project_name = "test-project-1"
role_name = "adminstrator"

project_data = keycloak_admin.get_group_by_path(
    path=f"projects/{project_name}/{role_name}"
)


project_uuid = project_data['id']

keycloak_admin.assign_group_realm_roles(
    group_id=project_uuid,
    roles=[], 
)