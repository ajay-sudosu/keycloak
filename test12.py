from keycloak import KeycloakAdmin

keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080",
    username="admin",
    password="admin",
    realm_name="skylus",
    user_realm_name="master",
)

# policy_id = keycloak_admin.get_client_authz_policy(
#     client_id="547b5d29-0f65-4392-b143-59e0ac1d6246",
#     policy_id="4cb412f5-7e09-49bd-921c-b73ccb1f7bcb",
# )

# policy_data = keycloak_admin.get_client_authz_permission_associated_policies(
#     client_id="547b5d29-0f65-4392-b143-59e0ac1d6246",
#     policy_id="4cb412f5-7e09-49bd-921c-b73ccb1f7bcb",
# )

# print(policy_data)



policy_data = keycloak_admin.get_client_authz_policy(
    client_id="547b5d29-0f65-4392-b143-59e0ac1d6246",
    policy_id="d15c6e96-894e-4980-aa95-d8f5c16ec164",
)

print(policy_data)
