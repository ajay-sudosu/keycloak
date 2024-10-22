from keycloak import KeycloakOpenID

openId = KeycloakOpenID(
    server_url="http://localhost:8080",
    realm_name="master",
    client_id="user-login",
    client_secret_key="",
)

token_admin = openId.token(
    username="admin",
    password="admin",
)


print(token_admin)
