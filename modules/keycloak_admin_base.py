from keycloak import KeycloakAdmin

from constants import env


class KeycloakAdminBase:

    def __init__(self):
        self.keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            user_realm_name=env.MASTER_REALM_NAME,
        )

    def get_client_uuid(
        self,
        client_name: str,
    ):
        return self.keycloak_admin.get_client_id(
            client_id=client_name,
        )

    def get_client_secrets(
        self,
        client_uuid: str,
    ):
        return self.keycloak_admin.get_client_secrets(
            client_id=client_uuid,
        )

    def delete_user(
        self,
        user_uuid: str,
    ):
        return self.keycloak_admin.delete_user(
            user_id=user_uuid,
        )

    def get_client_role_data(
        self,
        client_uuid: str,
        role_name: str,
    ):
        return self.keycloak_admin.get_client_role(
            client_id=client_uuid,
            role_name=role_name,
        )

    def get_user_social_logins(
        self,
        user_uuid: str,
    ):
        return self.keycloak_admin.get_user_social_logins(
            user_id=user_uuid,
        )

    def get_events(
        self,
        user_uuid: str | None = None,
        log_type: str | None = None,
    ):
        return self.keycloak_admin.get_events(
            query={
                "userId": user_uuid,
                "type": log_type,
            } if user_uuid is not None or log_type is not None else None
        )
