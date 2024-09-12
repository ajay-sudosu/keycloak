from modules.keycloak_admin_base import KeycloakAdminBase


class MicrosoftLogin(KeycloakAdminBase):

    def __init__(self, domain_name):
        super().__init__()
        self.keycloak_admin.change_current_realm(
            realm_name=domain_name,
        )
        self.domain_name = domain_name

    def check_email_against_domain_name(
        self,
        client_uuid: str,
        role_name: str,
        email: str,
    ):
        # fetch user-login client's attribute-role (role)
        role_attribute_data = self.get_client_role_data(
            client_uuid=client_uuid,
            role_name=role_name,
        )

        # white listed domains list
        white_listed_domains = role_attribute_data["attributes"]["domain"]

        # check if domain is in whitelisted domains
        return email.split("@")[-1] in white_listed_domains

    def check_for_user_microsoft_social_login(
        self,
        user_uuid: str,
    ):
        # get user social logins linked in identity provider of user
        user_social_logins = self.get_user_social_logins(
            user_uuid=user_uuid,
        )

        # check if microsoft is present in user linked identity providers
        for social_login in user_social_logins:
            if social_login["identityProvider"] == "microsoft":
                return True

        # microsoft is not present
        return False

    def check_for_microsoft_login_in_events(
        self,
        user_uuid: str,
    ):
        # get events
        user_login_events = self.get_events(
            user_uuid=user_uuid,
            log_type="LOGIN",
        )

        # latest user login event
        latest_user_login_event = user_login_events[0]

        # check for response_type
        if latest_user_login_event["details"].get("response_type", None) is not None:
            # check if user have microsoft login
            return self.check_for_user_microsoft_social_login(
                user_uuid=user_uuid,
            )

        return False
