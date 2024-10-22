from authentication.base.openid_base import OpenID

from constants import LoadEnv

# load env obj
load_env = LoadEnv()


class AdminOps(OpenID):

    def __init__(self):
        # init super class methods
        super().__init__(
            domain_name=load_env.get_variable('AUTH_SERVER_MASTER_REALM_NAME'),
            client_name=load_env.get_variable('AUTH_SERVER_USER_LOGIN_CLIENT_ID'),
        )

    def get_admin_access_token(
        self,
    ):
        """
        Return admin access token
        """
        # return admin access token
        return self.get_access_token(
            username=load_env.get_variable('AUTH_SERVER_ADMIN_USERNAME'),
            password=load_env.get_variable('AUTH_SERVER_ADMIN_PASSWORD'),
        )

    def logout_admin_access_token(
        self,
        refresh_token: str,
    ):
        """
        Logout admin access token
        """
        # return admin access token
        return self.logout_user(
            auth_header=refresh_token,
        )
