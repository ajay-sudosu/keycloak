import re
import requests
import json

from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakPostError
from constants import LoadEnv

# load env obj
load_env = LoadEnv()


class AdminBase:

    def __init__(self, domain_name):
        # keycloak_admin object
        self.keycloak_admin = KeycloakAdmin(
            server_url=load_env.get_variable("AUTH_SERVER_URL"),
            username=load_env.get_variable("AUTH_SERVER_ADMIN_USERNAME"),
            password=load_env.get_variable("AUTH_SERVER_ADMIN_PASSWORD"),
            user_realm_name=load_env.get_variable("AUTH_SERVER_MASTER_REALM_NAME"),
            realm_name=domain_name,
        )
        self.domain_name = domain_name

    def get_users(self, query: dict = None):
        return self.keycloak_admin.get_users(query=query)

    def get_client_uuid(
        self,
        client_name: str,
    ):
        """
        Get Client uuid based on client name
        """

        # return client uuid
        return self.keycloak_admin.get_client_id(
            client_id=client_name,
        )

    def get_current_domain(self):
        return self.keycloak_admin.get_current_realm()

    def realm_update(self, domain_name: str, payload: dict):
        return self.keycloak_admin.update_realm(realm_name=domain_name, payload=payload)

    def change_current_realm(
        self,
        realm_name: str,
    ):
        """
        Sets the current realm
        """

        # changes the current context realm
        return self.keycloak_admin.change_current_realm(
            realm_name=realm_name,
        )

    def get_client_secrets(
        self,
        client_name: str,
    ):
        """
        Get client secrets from client_name
        """

        # get client uuid
        client_uuid = self.get_client_uuid(
            client_name=client_name,
        )

        # return client secrets
        return self.keycloak_admin.get_client_secrets(
            client_id=client_uuid,
        )

    def delete_user(
        self,
        user_uuid: str,
    ):
        """
        Delete user by uuid
        """

        # deletes existing user by uuid
        return self.keycloak_admin.delete_user(
            user_id=user_uuid,
        )

    def get_client_role_data(
        self,
        client_name: str,
        role_name: str,
    ):
        """
        Get client's role data
        """

        # get client uuid
        client_uuid = self.keycloak_admin.get_client_id(
            client_name=client_name,
        )

        # get client
        return self.keycloak_admin.get_client_role(
            client_id=client_uuid,
            role_name=role_name,
        )

    def get_user_social_logins(
        self,
        user_uuid: str,
    ):
        """
        Get User linked identity providers by user_uuid
        """

        # return user identity providers info
        return self.keycloak_admin.get_user_social_logins(
            user_id=user_uuid,
        )

    def get_all_realm_roles(
        self,
        filter_default_roles: bool,
        domain_level: bool = False,
        project_level: bool = False,
    ):
        """
        Get all realm roles
        """
        # all realm roles
        all_realm_roles_data = self.keycloak_admin.get_realm_roles()

        # check for filter_default_roles true
        if filter_default_roles:
            # filtered realm roles (admin created)
            filtered_realm_roles_data = [
                x
                for x in all_realm_roles_data
                if not re.search(
                    r"^\$\{role_[a-zA-Z0-9_-]+\}",
                    x["description"],
                )
            ]

            # get all roles
            all_realm_roles_data = filtered_realm_roles_data.copy()

        # domain level roles
        if all_realm_roles_data and domain_level:
            # format for domain level roles list
            domain_level_roles = []

            # role in data
            for i, role in enumerate(all_realm_roles_data):
                # role detail
                role_detail = self.get_realm_role_by_id(
                    role_id=role["id"],
                )

                # check for domain level
                if role_detail["attributes"]["level"] == ["domain"]:
                    domain_level_roles.append(all_realm_roles_data[i])

            # replace with domain_level roles
            all_realm_roles_data = domain_level_roles.copy()

        # fitler for project level roles
        elif all_realm_roles_data and project_level:
            # project level roles list
            project_level_roles = []

            # role in data
            for i, role in enumerate(all_realm_roles_data):
                # role detail
                role_detail = self.get_realm_role_by_id(
                    role_id=role["id"],
                )

                # check for project level
                if role_detail["attributes"]["level"] == ["project"]:
                    project_level_roles.append(all_realm_roles_data[i])

            all_realm_roles_data = project_level_roles.copy()

        if all_realm_roles_data:
            for realm_role in all_realm_roles_data:
                realm_role.pop("composite")
                realm_role.pop("clientRole")
                realm_role.pop("containerId")
                realm_role["domain_id"] = self.keycloak_admin.get_current_realm()

        # return filtered realm roles (admin created)
        return all_realm_roles_data

    def regenerate_all_registered_service_client_creds(self, domain_name: str):
        """
        Regenerates all the registered service client creds
        """
        # loop through service-names list
        registered_services = json.loads(load_env["AUTH_SERVER_REGISTERED_SERVICES"])
        for service in registered_services:
            # client uuid
            client_uuid = self.keycloak_admin.get_client_id(
                client_id=service,
            )

            # generate new client secret cred
            self.keycloak_admin.generate_client_secrets(
                client_id=client_uuid,
            )

    def create_domain(self, domain_name: str):
        # change current realm
        self.change_current_realm(
            realm_name=load_env["AUTH_SERVER_RAW_TEMPLATE_NAME"],
        )

        template_realm_json = self.keycloak_admin.export_realm(
            export_clients=True, export_groups_and_role=True
        )

        realm_data = self.format_realm_json(
            realm_json=template_realm_json,
            domain_name=domain_name,
        )

        # upload to domain.json to keycloak server
        self.keycloak_admin.import_realm(
            payload=realm_data,
        )

        self.change_current_realm(
            realm_name=domain_name,
        )

        # regenerate client tokens
        self.regenerate_all_registered_service_client_creds(
            domain_name=domain_name,
        )

    # creating user in Auth server (keycloak)
    def user_create(self, username: str,
                    email: str,
                    password: str,
                    attr: dict,
                    meta_data: dict):
        attr["i_data"] = json.dumps(meta_data)
        user_create_payload = {
            "username": username,
            "email": email,
            "enabled": True,
            "firstName": username,
            "lastName": username,
            "attributes": attr,
            "emailVerified": True,
        }
        user_id = self.keycloak_admin.create_user(
            payload=user_create_payload, exist_ok=False
        )
        self.keycloak_admin.set_user_password(
            user_id=user_id, password=password, temporary=False
        )

        return user_id

    def update_user(self, user_id: str, **kwargs):
        """

        :param user_id:
        :param kwargs:
        - username: str
        - password: str
        - email: str
        :return:
        """
        if kwargs.get("password"):
            self.keycloak_admin.set_user_password(
                user_id=user_id, password=kwargs["password"], temporary=False
            )
            kwargs.pop("password")
        user_update_payload = {key: value for key, value in kwargs.items() if value is not None}
        user_update_payload["emailVerified"] = True
        user_update_payload["enabled"] = True
        self.keycloak_admin.update_user(user_id=user_id, payload=user_update_payload)

        return user_id

    def all_realms(self):
        return self.keycloak_admin.get_realms()

    def get_realm_by_name(self, domain_name):
        return self.keycloak_admin.get_realm(realm_name=domain_name)

    def remove_ids(self, data):
        # remove ids from all the fields
        if isinstance(data, dict):
            data.pop("id", None)
            data.pop("_id", None)
            data.pop("internalId", None)
            for key, value in data.items():
                self.remove_ids(value)
        elif isinstance(data, list):
            for item in data:
                self.remove_ids(item)

        return data

    def format_realm_json(
        self,
        realm_json: dict,
        domain_name: str,
    ):
        """
        Formats the existing realm to import as a new realm.
        """

        # remove all the ids
        realm_json = self.remove_ids(realm_json)

        # remove 'Default policy', 'Default Permission', and 'Default Resource'
        for auth_data_index, item in enumerate(realm_json["clients"]):
            if "authorizationSettings" in realm_json["clients"][auth_data_index]:
                # remove 'Default Policy', 'Default Permission'
                for policy_index, sub_item in enumerate(
                    realm_json["clients"][auth_data_index]["authorizationSettings"][
                        "policies"
                    ]
                ):
                    if sub_item["name"] == "Default Policy":
                        realm_json["clients"][auth_data_index]["authorizationSettings"][
                            "policies"
                        ].pop(policy_index)

                for policy_index, sub_item in enumerate(
                    realm_json["clients"][auth_data_index]["authorizationSettings"][
                        "policies"
                    ]
                ):
                    if sub_item["name"] == "Default Permission":
                        realm_json["clients"][auth_data_index]["authorizationSettings"][
                            "policies"
                        ].pop(policy_index)

                # remove 'Default Resource'
                for resource_index, sub_item in enumerate(
                    realm_json["clients"][auth_data_index]["authorizationSettings"][
                        "resources"
                    ]
                ):
                    if sub_item["name"] == "Default Resource":
                        realm_json["clients"][auth_data_index]["authorizationSettings"][
                            "resources"
                        ].pop(resource_index)

        # set domain_name as realm name
        realm_json["realm"] = domain_name

        # return formatted json
        return realm_json

    def create_a_realm_role(
        self,
        role_name: str,
        description: str,
        level: str,
    ):
        """
        Create a custom realm role
        """
        # create a role
        return self.keycloak_admin.create_realm_role(
            payload={
                "name": role_name,
                "description": description,
                "attributes": {
                    "level": [level],
                }
            }
        )

    def delete_a_realm_role(
        self,
        role_name: str,
    ):
        """
        Delete a realm role
        """
        # delete a realm role
        return self.keycloak_admin.delete_realm_role(
            role_name=role_name,
        )

    def update_a_realm_role(
        self,
        role_name: str,
        payload: dict,
    ):
        """
        Update a realm role
        """
        # update a realm role
        return self.keycloak_admin.update_realm_role(
            role_name=role_name,
            payload=payload,
        )

    def get_user_uuid(
        self,
        username: str,
    ):
        """
        Get user uuid by username
        """

        # return user uuid
        return self.keycloak_admin.get_user_id(
            username=username,
        )

    def get_user_by_user_id(
        self,
        user_uuid: str,
    ):
        """
        Get user data by user id
        """
        # return user detail by user id
        return self.keycloak_admin.get_user(
            user_id=user_uuid,
        )

    def assign_realm_role_to_a_user(
        self,
        username: str,
        role_names: list[str],
    ):
        """
        Assign a realm role to a user
        """
        # get user uuid by username
        user_uuid = self.get_user_uuid(
            username=username,
        )

        # list of realm roles obj
        roles_list = []

        # prepares roles obj list
        for role_name in role_names:
            roles_list.append(
                self.keycloak_admin.get_realm_role(
                    role_name=role_name,
                )
            )

        # assign role to the user
        return self.keycloak_admin.assign_realm_roles(
            user_id=user_uuid,
            roles=roles_list,
        )

    def unassign_realm_role_from_a_user(
        self,
        username: str,
        role_names: list[str],
    ):
        """
        Un-assign a realm role from a user
        """

        # get user uuid by username
        user_uuid = self.get_user_uuid(
            username=username,
        )

        # list of realm roles obj
        roles_list = []

        # prepares roles obj list
        for role_name in role_names:
            roles_list.append(
                self.keycloak_admin.get_realm_role(
                    role_name=role_name,
                )
            )

        # remove roles from user
        return self.keycloak_admin.delete_realm_roles_of_user(
            user_id=user_uuid,
            roles=roles_list,
        )

    def get_all_client_policies(
        self,
        client_name: str,
        filter_default_policies: bool = False,
    ):
        """
        Get all policies of a client
        """
        # get all policies
        client_uuid = self.get_client_uuid(
            client_name=client_name,
        )

        # get all policies
        policies_list = self.keycloak_admin.get_client_authz_policies(
            client_id=client_uuid,
        )

        # check for filter polices list
        if policies_list and filter_default_policies:
            # temporary policy list
            filtered_policy_list = [x for x in policies_list if x['name'] != "Default Policy"]
            policies_list = filtered_policy_list.copy()

        # return policies list
        return policies_list

    def update_roles_to_a_policy(
        self,
        admin_token: str,
        realm_name: str,
        client_uuid: str,
        policy_uuid: str,
        payload: dict,
    ):
        """
        Attach/Detach a policy to a role
        """
        # api URL
        URL = f"{load_env.get_variable('AUTH_SERVER_URL')}/admin/realms/{realm_name}/clients/{client_uuid}/authz/resource-server/policy/role/{policy_uuid}"

        # headers
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-type": "application/json",
        }

        # payload
        payload = payload

        # send request
        response = requests.put(
            url=URL,
            headers=headers,
            json=payload,
            timeout=30,
        )

        # return response
        return response.text

    def get_policy_detail_by_name(
        self,
        admin_token: str,
        policy_name: str,
        realm_name: str,
        client_uuid: str,
    ):
        """
        Get Policy Detail
        """
        # api url
        URL = f"{load_env.get_variable('AUTH_SERVER_URL')}/admin/realms/{realm_name}/clients/{client_uuid}/authz/resource-server/policy/search"

        # query_params
        query_params = {
            "name": policy_name,
        }

        # headers
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-type": "application/json",
        }

        # hit detail api
        response = requests.get(
            url=URL,
            params=query_params,
            headers=headers,
            timeout=30,
        )

        # return response
        return response.json()

    def get_policy_detail_by_id(
        self,
        client_uuid: str,
        policy_id: str,
    ):
        """Policy detail by id"""
        # get policy detail
        return self.keycloak_admin.get_client_authz_policy(
            client_id=client_uuid,
            policy_id=policy_id,
        )

    def get_realm_role_by_name(
        self,
        role_name: str,
    ):
        """
        Get Realm role data
        """
        # get realm role data
        return self.keycloak_admin.get_realm_role(
            role_name=role_name,
        )

    def get_realm_base(self, domain_name):
        return self.keycloak_admin.get_realm(realm_name=domain_name)

    def delete_realm(self, realm_name):
        return self.keycloak_admin.delete_realm(realm_name=realm_name)

    def get_realm_role_by_id(
        self,
        role_id: str,
    ):
        """
        Get Realm role data by role-id
        """
        # get realm role data
        return self.keycloak_admin.get_realm_role_by_id(
            role_id=role_id,
        )

    def get_current_realm_role_of_user(
        self,
        user_uuid: str,
        filter_default_roles: bool,
        domain_level: bool = False,
        project_level: bool = False,
    ):
        """
        Get current realm roles of user.
        """
        # all realm roles data
        realm_roles = self.keycloak_admin.get_realm_roles_of_user(
            user_id=user_uuid,
        )

        # filter default roles
        if filter_default_roles:
            # filtered realm roles (admin created)
            filtered_realm_roles_data = [
                x
                for x in realm_roles
                if not re.search(
                    r"^\$\{role_[a-zA-Z0-9_-]+\}",
                    x["description"],
                )
            ]

            # updated realm roles
            realm_roles = filtered_realm_roles_data.copy()

        # get realm roles (domain_level)
        if realm_roles and domain_level:
            # fetch domain_level roles
            for role in realm_roles:
                # get role detail
                role_detail = self.get_realm_role_by_id(
                    role_id=role["id"],
                )

                # realm_roles
                if role_detail["attributes"]["level"] == ["domain"]:
                    # get realm role
                    return role_detail

        # get realm roles (project_level)
        if realm_roles and project_level:
            # fetch domain_level roles
            for role in realm_roles:
                # get role detail
                role_detail = self.get_realm_role_by_id(
                    role_id=role["id"],
                )

                # realm_roles
                if role_detail["attributes"]["level"] == ["project"]:
                    # get realm role
                    return role_detail

        # return user domain role data
        return realm_roles if realm_roles else {}

    def get_all_groups(self, query: dict = None):
        return self.keycloak_admin.get_groups()

    def create_group_role_by_path(
        self,
        group_name: str,
        parent_group_uuid: str,
        role_id: str,
    ):
        """
        Create a group
        """
        # create group
        group_uuid = self.keycloak_admin.create_group(
            payload={
                "name": group_name,
            },
            parent=parent_group_uuid,
        )

        # assign role on user
        self.keycloak_admin.assign_group_realm_roles(
            group_id=group_uuid,
            roles=[{'id': role_id, 'name': group_name}],
        )

    def assign_role_on_group(self, group_uuid: str, role_id: str, group_name: str):
        return self.keycloak_admin.assign_group_realm_roles(
            group_id=group_uuid,
            roles=[{'id': role_id, 'name': group_name}],
        )

    def get_group_data_by_full_path(
        self,
        group_path: str,
    ):
        """
        Get group name by full path
        """
        # get group name by id
        return self.keycloak_admin.get_group_by_path(
            path=group_path,
        )

    def add_metadata_to_group(
        self,
        group_path: str,
        data: dict,
    ):
        """
        Metadata to group
        """
        # get group uuid
        group_data = self.get_group_data_by_full_path(
            group_path=group_path,
        )

        # group uuid
        group_id = group_data["id"]

        # group name
        group_name = group_data["name"]

        # payload
        payload = {
            "name": group_name,
            "attributes": data,
        }

        # add metadata to group
        return self.keycloak_admin.update_group(
            group_id=group_id,
            payload=payload,
        )

    # def get_all_groups(
    #     self,
    #     parent_group_path: str,
    # ):
    #     """
    #     Get all child groups
    #     """
    #     # get all ching groups
    #     return self.keycloak_admin.get_subgroups(
    #         path=parent_group_path,
    #     )

    def add_user_to_group(
        self,
        group_uuid: str,
        user_uuid: str,
    ):
        """
        Add a user to group
        """
        # add user to group
        return self.keycloak_admin.group_user_add(
            user_id=user_uuid,
            group_id=group_uuid,
        )

    def remove_user_from_group(
        self,
        group_uuid: str,
        user_uuid: str,
    ):
        """Remove user from a group"""
        # remove user from given group
        return self.keycloak_admin.group_user_remove(
            user_id=user_uuid,
            group_id=group_uuid,
        )

    def get_group_by_id(
        self,
        group_uuid: str,
    ):
        """
        Get group data by uuid
        """
        # return group uuid
        return self.keycloak_admin.get_group(
            group_id=group_uuid,
        )

    def get_groups_by_realm_role(
        self,
        role_name: str,
    ):
        """
        Get group names by realm role
        """
        # return group list of realm_role
        return self.keycloak_admin.get_realm_role_groups(
            role_name=role_name,
        )

    def create_group(self, parent, payload):
        return self.keycloak_admin.create_group(payload=payload, parent=parent)

    def update_group(self, group_id: str, payload: dict):
        self.keycloak_admin.update_group(group_id=group_id, payload=payload)

    def delete_group(
        self,
        group_uuid: str,
    ):
        # delete group
        self.keycloak_admin.delete_group(
            group_id=group_uuid,
        )

    def get_users_of_realm_role(
        self,
        role_name: str,
    ):
        """
        get users of realm role
        """
        return self.keycloak_admin.get_realm_role_members(
            role_name=role_name,
        )

    def update_group_name(
        self,
        group_uuid: str,
        updated_group_name: str,
    ):
        """
        update group name
        """
        return self.keycloak_admin.update_group(
            group_id=group_uuid,
            payload={
                "name": updated_group_name,
            }
        )

    def get_all_users_of_group(self, group_uuid):
        """
        Get all users of group
        :param group_uuid:
        :return:
        """
        # fetch all users in the group
        return self.keycloak_admin.get_group_members(
            group_id=group_uuid,
        )

    def get_groups_of_user(
        self,
        user_uuid: str,
    ):
        """
        Get all groups of user
        """
        return self.keycloak_admin.get_user_groups(
            user_id=user_uuid,
        )

    def get_resource_data(
        self,
        admin_token: str,
        resource_name: str,
        realm_name: str,
        client_uuid: str,
    ):
        """Fetch Resource Detail"""
        # url
        URL = f"{load_env['AUTH_SERVER_URL']}/admin/realms/{realm_name}/clients/{client_uuid}/authz/resource-server/resource/search"

        # headers
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-type": "application/json",
        }

        # query params
        query_params = {
            "name": resource_name,
        }

        # send request
        response = requests.get(
            url=URL,
            headers=headers,
            params=query_params,
            timeout=30,
        )

        # return response
        if response.status_code == 200:
            return response.json()
        else:
            return response.text

    def get_all_groups_of_user(
        self,
        user_uuid: str,
        query: dict | None = None,
    ):
        """
        User groups
        """
        # return user groups
        return self.keycloak_admin.get_user_groups(
            user_id=user_uuid,
            query=query,
        )

    def get_all_permissions(
        self,
        client_uuid: str,
    ):
        """
        Fetch all the permissions
        """
        # get permissions
        return self.keycloak_admin.get_client_authz_permissions(
            client_id=client_uuid,
        )

    def get_permissions_of_resource(
        self,
        admin_token: str,
        resource_uuid: str,
        realm_name: str,
        client_uuid: str,
    ):
        URL = f"{load_env['AUTH_SERVER_URL']}/admin/realms/{realm_name}/clients/{client_uuid}/authz/resource-server/resource/{resource_uuid}/permissions"

        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-type": "application/json",
        }

        response = requests.get(
            url=URL,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:
            return response.json()
        else:
            return response.text

    def check_permission_by_scope(
        self,
        realm_name: str,
        client_uuid: str,
        admin_token: str,
        resource_scope: str,
        permission_id: str,
    ):
        """Permission Detail"""
        # return permission detail
        URL = f"{load_env['AUTH_SERVER_URL']}/admin/realms/{realm_name}/clients/{client_uuid}/authz/resource-server/permission"

        # headers
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-type": "application/json",
        }

        # query params
        query_params = {
            "scope": resource_scope,
            "policyId": permission_id,
        }

        # permission data
        response = requests.get(
            url=URL,
            headers=headers,
            params=query_params,
        )

        # if status code
        if response.status_code == 200:
            if response.json() == []:
                return False
            else:
                return True

        return response.text

    def get_permission_associated_policy(
        self,
        client_uuid: str,
        permission_id: str,
    ):
        """Fetch permission associated policy"""
        # permission associated policy
        return self.keycloak_admin.get_client_authz_permission_associated_policies(
            client_id=client_uuid,
            policy_id=permission_id,
        )

    def reset_kc_user_password(
        self,
        user_id: str,
        password: str,
    ):
        """Reset KC User password"""
        # reset password
        return self.keycloak_admin.set_user_password(
            user_id=user_id,
            password=password,
            temporary=False,
        )

    def get_user_kc_creds(
        self,
        user_id: str,
    ):
        """Get user current password"""
        # get current password
        return self.keycloak_admin.get_credentials(
            user_id=user_id,
        )
