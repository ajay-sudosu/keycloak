from authentication.base.admin_base import AdminBase
from keycloak import KeycloakOpenID

from constants import LoadEnv

# load env obj
load_env = LoadEnv()


class OpenID(AdminBase):
    def __init__(
        self,
        domain_name: str,
        client_name: str,
    ):
        """
        OpenId methods
        """
        # get super class objects
        super().__init__(domain_name=domain_name)

        # get client secrets
        client_secret_key = self.get_client_secrets(
            client_name=client_name,
        )

        # openId obj
        self.openID = KeycloakOpenID(
            server_url=load_env.get_variable('AUTH_SERVER_URL'),
            realm_name=domain_name,
            client_id=client_name,
            client_secret_key=client_secret_key['value'],
        )


    def get_access_token(self, username, password):
        return self.openID.token(
            username=username,
            password=password,
        )

    def get_refresh_token(self, auth_header: str):
        return self.openID.refresh_token(
            refresh_token=auth_header,  # noqa: E501
            grant_type=["refresh_token"],
        )
        # return self.openID.refresh_token(
        #     refresh_token=request.headers.get("Authorization").replace(
        #         "Bearer ",
        #         "",
        #     ),  # noqa: E501
        #     grant_type=["refresh_token"],
        # )

    def logout_user(self, auth_header: str):
        return self.openID.logout(refresh_token=auth_header)
        # return keycloak_openid.logout(
        #     refresh_token=request.headers.get("Authorization").replace(
        #         "Bearer ", ""
        #     )  # noqa: E501
        # )

    def handshake_code(self, code: str):
        return self.openID.token(
            code=code,
            grant_type=["authorization_code"],
            redirect_uri=load_env.get_variable('AUTH_SERVER_TOKEN_GENERATE_API_URL'),
        )

    def user_info(self, token: str):
        return self.openID.userinfo(token=token)

    def sign_in_redirect(self):
        return self.openID.auth_url(
            redirect_uri=load_env.get_variable('AUTH_SERVER_TOKEN_GENERATE_API_URL'),
            scope="openid email profile",
        )

    def check_uma_access(
        self,
        token: str,
        keycloak_uma_per_list,
    ):
        """
        returns if token has access for endpoint
        """
        return self.openID.has_uma_access(
            token=token,
            permissions=keycloak_uma_per_list,
        )

    def refresh_token(
        self,
        token: str,
    ):
        """
        refresh access token
        """
        # return refresh access token
        return self.openID.refresh_token(
            refresh_token=token,
        )
