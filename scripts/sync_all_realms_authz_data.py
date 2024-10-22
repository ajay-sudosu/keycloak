""""
Script will sync all the authorization data of all the registered services from 'raw-template'.
"""

import json
from authentication.base.admin_ops import AdminOps
from authentication.role_ops.policy_ops import PolicyOps

from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError
import requests

adminOps = AdminOps()
policyOps = PolicyOps(domain_name="raw-template")

AUTH_SERVER_URL = "http://10.233.0.149:30446"  # change it to kc url ex: http://<ip>:port


REGISTERED_CLIENTS_WITH_AUTH = [
    "auth-service",
    "billing-service",
    "compute-service",
    "network-service",
    "storage-service",
]

NEGLECT_REALMS = [
    "master",
    "raw-template",
    "test_realm"
]

keycloak_admin = KeycloakAdmin(
    server_url=AUTH_SERVER_URL,
    username="admin",
    password="admin",
    user_realm_name="master",
    realm_name="raw-template",
)


def get_authz_data(
    admin_token: str, client_uuid: str, realm_name: str, client_name: str
) -> dict:
    URL = f"{AUTH_SERVER_URL}/admin/realms/{realm_name}/clients/{client_uuid}/authz/resource-server/settings"

    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {admin_token}",
    }

    response = requests.get(
        url=URL,
        headers=headers,
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"Failed to fetch authz data for client: {client_uuid}, realm: {realm_name}"
        )
        return None


def import_all_clients_updated_info_into_all_realms():
    # admin access token
    admin_token = adminOps.get_admin_access_token()

    # get all realms
    all_realms = keycloak_admin.get_realms()

    # client data
    client_data_list = []

    # get client data from raw-template
    for service_client in REGISTERED_CLIENTS_WITH_AUTH:
        # client uuid
        client_uuid = keycloak_admin.get_client_id(
            client_id=service_client,
        )

        # get settings data
        authz_data = get_authz_data(
            admin_token=admin_token["access_token"],
            client_uuid=client_uuid,
            realm_name="raw-template",
            client_name=service_client,
        )

        # add it to list
        client_data_list.append(authz_data)

    for realm_data in all_realms:
        if realm_data["realm"] not in NEGLECT_REALMS:
            # set current realm
            keycloak_admin.change_current_realm(
                realm_name=realm_data["realm"],
            )

            # import client data
            for i, service_client in enumerate(REGISTERED_CLIENTS_WITH_AUTH):
                # client data
                client_authz_data = client_data_list[i]

                # logging
                print(
                    f"Processing: tenant: {realm_data['realm']} - service: {service_client}"
                )

                try:
                    # client uuid
                    client_uuid = keycloak_admin.get_client_id(
                        client_id=service_client,
                    )

                    # export data
                    export_data = "presents"
                except KeycloakGetError:
                    # set export data to none
                    export_data = None

                if export_data and authz_data:
                    # url
                    URL = f"{AUTH_SERVER_URL}/admin/realms/{realm_data['realm']}/clients/{client_uuid}/authz/resource-server/import"

                    # change realm
                    keycloak_admin.change_current_realm(
                        realm_name=realm_data["realm"],
                    )

                    # headers
                    headers = {
                        "Content-type": "application/json",
                        "Authorization": f"Bearer {admin_token['access_token']}",
                    }

                    # request post
                    response = requests.post(
                        url=URL,
                        headers=headers,
                        json=client_authz_data,
                        timeout=30,
                    )

                    # check response status
                    if response.status_code == 204:
                        # # change context domain of policy obj roles
                        # policyOps.change_current_realm(
                        #     realm_name=realm_data["realm"],
                        # )

                        # # set policy domain name
                        # policyOps.domain_name = realm_data['realm']

                        # # iterate through all policies
                        # for policy_data in client_authz_data["policies"]:
                        #     # get roles

                        #     # check for roles key
                        #     if policy_data['config'].get('roles'):

                        #         # get all role data
                        #         roles_list = json.loads(policy_data['config']["roles"])

                        #         # iterate through all roles
                        #         for role_data in roles_list:
                        #             # role_names
                        #             role_names = [role_data['id']]

                        #             # get policy id by name
                        #             policyOps.assign_role_to_a_policy(
                        #                 client_name=service_client,
                        #                 policy_name=policy_data["name"],
                        #                 role_names=role_names,
                        #             )

                        print(
                            f"Updated tenant: {realm_data['realm']} - service: {service_client}"
                        )
                    else:
                        print(
                            f"Failed to update tenant: {realm_data['realm']} - service: {service_client}"
                        )

                        print(response.status_code, response.text)

                else:
                    # print client not found
                    print(f"Service (client): {service_client} not found")

    # logout admin token
    adminOps.logout_admin_access_token(refresh_token=admin_token["refresh_token"])


# update all clients
import_all_clients_updated_info_into_all_realms()


# print end
print("Updated all realms!")
