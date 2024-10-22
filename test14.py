from keycloak import KeycloakAdmin

keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080",
    username="admin",
    password="admin",
    realm_name="master",
)

keycloak_admin.create_client(
    payload={
        "protocol": "openid-connect",
        "clientId": "user-login",
        "name": "user-login",
        "description": "",
        "publicClient": False,
        "authorizationServicesEnabled": True,
        "serviceAccountsEnabled": True,
        "implicitFlowEnabled": False,
        "directAccessGrantsEnabled": True,
        "standardFlowEnabled": True,
        "frontchannelLogout": True,
        "attributes": {
            "saml_idp_initiated_sso_url_name": "",
            "oauth2.device.authorization.grant.enabled": False,
            "oidc.ciba.grant.enabled": False
        },
        "alwaysDisplayInConsole": True,
        "rootUrl": "",
        "baseUrl": ""
    },
    skip_exists=True,
)
