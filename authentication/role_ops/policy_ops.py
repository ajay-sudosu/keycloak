import json

from keycloak.exceptions import KeycloakError
from dependency.exceptions import AuthExceptions
from authentication.base.admin_base import AdminBase
from authentication.base.admin_ops import AdminOps

from constants import LoadEnv

# load env
load_env = LoadEnv()


class PolicyOps(AdminBase):

    def __init__(self, domain_name):
        try:
            # init super class methods
            super().__init__(domain_name=domain_name)

            # set context domain
            self.change_current_realm(
                realm_name=domain_name,
            )

            # domain_name
            self.domain_name = domain_name

            # admin_token_obj
            self.admin_ops = AdminOps()
        except KeycloakError as ke_:
            if type(ke_.error_message) is bytes:
                # error dict str(byte to str)
                error_byte_str = ke_.error_message

                # error dict str
                error_dict_str = error_byte_str.decode("utf-8")

                # str to dict
                error_response_dict = json.loads(error_dict_str)

                # error message
                error_message = error_response_dict['error']
            else:
                # error message
                error_message = ke_.error_message

            if "realm not found" in error_message.lower():
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message="Domain not found."
                )
            elif "could not find client" in error_message.lower():
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message="Service not found!",
                )
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )


    def assign_role_to_a_policy(
        self,
        client_name: str,
        policy_name: str,
        role_names: list[str],
    ):
        try:
            # get client uuid
            client_uuid = self.get_client_uuid(
                client_name=client_name,
            )

            # get admin access token
            admin_token_data = self.admin_ops.get_admin_access_token()

            # get policy_data
            policy_api_data = self.get_policy_detail_by_name(
                admin_token=admin_token_data["access_token"],
                policy_name=policy_name,
                realm_name=self.domain_name,
                client_uuid=client_uuid,
            )

            # policy_uuid
            policy_uuid = policy_api_data["id"]

            # roles list existing
            roles_list = json.loads(policy_api_data["config"].get("roles"))

            # get role ids
            new_roles_list = []

            for role_name in role_names:
                # get role data
                role_data = self.get_realm_role_by_name(
                    role_name=role_name,
                )

                # get role id
                role_id = role_data["id"]

                new_roles_list.append(
                    {
                        "id": role_id,
                        "required": False,
                    }
                )

            # extend roles list
            roles_list.extend(new_roles_list)

            # result roles to be updated
            result_roles_list = []

            # filtered repeated roles
            for role_data in roles_list:
                # check for repeated roles
                if role_data not in result_roles_list:
                    result_roles_list.append(role_data)

            # prepare update payload
            update_payload = policy_api_data
            update_payload["fetchRoles"] = policy_api_data["config"].get("fetchRoles")
            update_payload["roles"] = roles_list
            update_payload.pop("config")
            update_payload["policies"] = []

            # call update function
            self.update_roles_to_a_policy(
                admin_token=admin_token_data["access_token"],
                realm_name=self.domain_name,
                client_uuid=client_uuid,
                policy_uuid=policy_uuid,
                payload=update_payload,
            )

            # logout refresh token
            self.admin_ops.logout_admin_access_token(
                refresh_token=admin_token_data["refresh_token"],
            )
        except KeycloakError as ke_:
            if type(ke_.error_message) is bytes:
                # error dict str(byte to str)
                error_byte_str = ke_.error_message

                # error dict str
                error_dict_str = error_byte_str.decode("utf-8")

                # str to dict
                error_response_dict = json.loads(error_dict_str)

                # error message
                error_message = error_response_dict['error']
            else:
                # error message
                error_message = ke_.error_message

            if "realm not found" in error_message.lower():
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message="Domain not found."
                )
            elif "could not find client" in error_message.lower():
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message="Service not found!",
                )
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def remove_role_from_a_policy(
        self,
        client_name: str,
        policy_name: str,
        role_names: str,
    ):
        try:
            # get client id
            client_uuid = self.get_client_uuid(
                client_name=client_name,
            )

            # get admin access token
            admin_token_data = self.admin_ops.get_admin_access_token()

            # get policy_data
            policy_api_data = self.get_policy_detail_by_name(
                admin_token=admin_token_data["access_token"],
                policy_name=policy_name,
                realm_name=self.domain_name,
                client_uuid=client_uuid,
            )

            # policy_uuid
            policy_uuid = policy_api_data["id"]

            # roles list existing
            roles_list = json.loads(policy_api_data["config"].get("roles"))

            # loop through roles
            for role_name in role_names:
                # get role data
                role_data = self.get_realm_role_by_name(
                    role_name=role_name,
                )

                # get role id
                role_id = role_data["id"]

                # role entry
                role_entry = {
                    "id": role_id,
                    "required": False,
                }

                # delete entry from roles list
                if role_entry in roles_list:
                    roles_list.remove(role_entry)

            # prepare update payload
            update_payload = policy_api_data
            update_payload["fetchRoles"] = policy_api_data["config"].get("fetchRoles")
            update_payload["roles"] = roles_list
            update_payload.pop("config")
            update_payload["policies"] = []

            # call update function
            self.update_roles_to_a_policy(
                admin_token=admin_token_data["access_token"],
                realm_name=self.domain_name,
                client_uuid=client_uuid,
                policy_uuid=policy_uuid,
                payload=update_payload,
            )

            # logout refresh token
            self.admin_ops.logout_admin_access_token(
                refresh_token=admin_token_data["refresh_token"],
            )
        except KeycloakError as ke_:
            if type(ke_.error_message) is bytes:
                # error dict str(byte to str)
                error_byte_str = ke_.error_message

                # error dict str
                error_dict_str = error_byte_str.decode("utf-8")

                # str to dict
                error_response_dict = json.loads(error_dict_str)

                # error message
                error_message = error_response_dict['error']
            else:
                # error message
                error_message = ke_.error_message

            if "realm not found" in error_message.lower():
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message="Domain not found."
                )
            elif "could not find client" in error_message.lower():
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message="Service not found!",
                )
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def get_all_policies(
        self,
        client_name: str,
    ):
        """
        Get all policies
        """
        try:
            # get all policies
            return self.get_all_client_policies(
                client_name=client_name,
                filter_default_policies=True,
            )
        except KeycloakError as ke_:
            if type(ke_.error_message) is bytes:
                # error dict str(byte to str)
                error_byte_str = ke_.error_message

                # error dict str
                error_dict_str = error_byte_str.decode("utf-8")

                # str to dict
                error_response_dict = json.loads(error_dict_str)

                # error message
                error_message = error_response_dict['error']
            else:
                # error message
                error_message = ke_.error_message

            if "realm not found" in error_message.lower():
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message="Domain not found."
                )
            elif "could not find client" in error_message.lower():
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message="Service not found!",
                )
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )
