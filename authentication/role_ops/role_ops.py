import re
import json

from dependency.exceptions import AuthExceptions
from keycloak.exceptions import KeycloakError
from authentication.base.admin_base import AdminBase


class RoleOps(AdminBase):
    """
    Consits of Role operation methods
    """

    def __init__(self, domain_name: str):
        # access super class methods
        try:
            super().__init__(domain_name=domain_name)

            # set context domain
            self.change_current_realm(
                realm_name=domain_name,
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def get_all_roles(
        self,
        filter_default_roles: bool,
        domain_level: bool = False,
        project_level: bool = False,
    ) -> list[dict]:
        """
        Get all roles
        """
        try:
            # return all roles as a list[dict]
            return self.get_all_realm_roles(
                filter_default_roles=filter_default_roles,
                domain_level=domain_level,
                project_level=project_level,
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def get_user_data_by_id(
        self,
        user_uuid: str,
    ):
        """Get user data by user id"""
        try:
            # return user data
            return self.get_user_by_user_id(
                user_uuid=user_uuid,
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def get_tenant_role_by_id(
        self,
        role_uuid: str,
    ):
        """
        Role Detail Method
        """
        try:
            return self.get_realm_role_by_id(
                role_id=role_uuid,
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def create_a_role_on_domain(
        self,
        role_name: str,
        description: str,
    ):
        """
        Create a role in a domain
        """
        try:
            # create a role
            return self.create_a_realm_role(
                role_name=role_name,
                description=description,
                level="domain",
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def delete_a_role_on_domain(
        self,
        role_name: str,
    ):
        """
        Delete a role
        """
        try:
            # delete a role/group of roles
            self.delete_a_realm_role(
                role_name=role_name,
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def update_a_role_of_domain(
        self,
        role_name: str,
        updated_role_name: str,
        updated_description: str,
    ):
        """
        Update a role name
        """
        try:
            # payload
            payload = {
                "name": updated_role_name if updated_role_name else role_name,
                "description": updated_description,
                "attributes": {
                    "level": ["domain"],
                },
            }

            # updated payload
            updated_payload = {k: v for k, v in payload.items() if v is not None}

            # update a role name
            return self.update_a_realm_role(
                role_name=role_name,
                payload=updated_payload,
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def assign_a_role(
        self,
        username: str,
        role_names: str | list[str],
    ):
        """
        Assign a role of group of roles to a user
        """
        try:
            # type check fo role_name as str
            # convert to list
            if type(role_names) is str:
                role_names = [role_names]

            # assign role(s) to user
            self.assign_realm_role_to_a_user(
                username=username,
                role_names=role_names,
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def unassign_role_from_user(
        self,
        username,
        role_names: str,
    ):
        """
        Un-assign a role/group of roles from user
        """
        try:
            # type check for role_name as str
            # convert to list
            if type(role_names) is str:
                role_names = [role_names]

            # unassign role(s) from a user
            return self.unassign_realm_role_from_a_user(
                username=username,
                role_names=role_names,
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def get_current_user_role_on_domain(
        self,
        user_uuid: str,
    ):
        """
        Get Current user role on domain.
        """
        try:
            # get user current realm role
            return self.get_current_realm_role_of_user(
                user_uuid=user_uuid,
                domain_level=True,
                filter_default_roles=True,
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def create_role_on_project(
        self,
        role_name: str,
        description: str,
    ):
        """
        Create a role on project level
        """
        try:
            return self.create_a_realm_role(
                role_name=role_name, description=description, level="project"
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def update_a_role_of_project(
        self,
        role_name: str,
        updated_role_name: str,
        updated_description: str,
    ):
        """
        Update a role name of project
        """
        try:
            # payload
            payload = {
                "name": updated_role_name if updated_role_name else role_name,
                "description": updated_description,
                "attributes": {
                    "level": ["project"],
                },
            }

            # updated payload
            updated_payload = {k: v for k, v in payload.items() if v is not None}

            if updated_role_name:
                # update all group names
                all_groups = self.get_groups_by_realm_role(
                    role_name=role_name,
                )

                for group_data in all_groups:
                    # remove all groups
                    self.update_group_name(
                        group_uuid=group_data["id"],
                        updated_group_name=updated_role_name,
                    )

            # update a role name
            return self.update_a_realm_role(
                role_name=role_name,
                payload=updated_payload,
            )
        except KeycloakError as ke_:
            print(ke_.error_message)
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def delete_a_role_on_project(
        self,
        role_name: str,
    ):
        """
        Delete a role on project
        """
        try:
            # get parent groups where this role is there
            all_projects_data = self.get_groups_by_realm_role(
                role_name=role_name,
            )

            # check for role in project
            for project_data in all_projects_data:
                # delete group
                self.delete_group(group_uuid=project_data["id"])

            # delete the realm role
            return self.delete_a_realm_role(
                role_name=role_name,
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def check_for_users_in_project_role(self, role_name) -> bool:
        """
        Check for any user in project role
        """
        try:
            # check for realm_role groups
            realm_role_groups = self.get_groups_by_realm_role(
                role_name=role_name,
            )

            # check for users in group
            for group_data in realm_role_groups:
                users_in_group = self.get_all_users_of_group(
                    group_uuid=group_data["id"],
                )

                if users_in_group != []:
                    return True

            # return true
            return False
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )

    def get_current_user_project_role(
        self,
        user_uuid: str,
        project_id: str,
    ):
        """
        Get User project role by given project
        """
        try:
            # get user group in the project
            all_groups_data_of_user = self.get_groups_of_user(
                user_uuid=user_uuid,
            )

            # filter the data for required project roles
            filtered_role_data = [
                x
                for x in all_groups_data_of_user
                if re.search(rf"^/projects/{re.escape(project_id)}/", x["path"])
            ]

            # realm role list
            realm_roles_data = []

            for role_data in filtered_role_data:
                realm_role_data = self.get_realm_role_by_name(
                    role_name=role_data["name"],
                )

                # append to main data
                realm_roles_data.append(realm_role_data)

            # return realm_roles data
            return realm_roles_data
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
            else:
                # raise auth exception
                raise AuthExceptions(
                    status_code=ke_.response_code,
                    message=error_message,
                )
