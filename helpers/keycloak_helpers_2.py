from keycloak import KeycloakAdmin
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from constants import env


def remove_ids(data):
    # remove ids from all the fields
    if isinstance(data, dict):
        data.pop("id", None)
        data.pop("_id", None)
        for key, value in data.items():
            remove_ids(value)
    elif isinstance(data, list):
        for item in data:
            remove_ids(item)

    return data


def format_realm_json(
    realm_json: dict,
    domain_name: str,
    ldap_user_name: str,
    ldap_user_password: str,
):
    """
    Formats the existing realm to import as a new realm.
    """

    # remove all the ids
    realm_json = remove_ids(realm_json)

    # remove 'Default policy', 'Default Permission', and 'Default Resource'
    for auth_data_index, item in enumerate(realm_json["clients"]):
        if "authorizationSettings" in realm_json["clients"][auth_data_index]:
            # remove 'Default Policy', 'Default Permission'
            for policy_index, sub_item in enumerate(
                realm_json["clients"][auth_data_index]["authorizationSettings"][
                    "policies"
                ]
            ):
                if (
                    sub_item["name"] == "Default Policy"
                    or sub_item["name"] == "Default Permission"
                ):
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

    # configure ldap settings
    for db_ind, item in enumerate(
        realm_json["components"]["org.keycloak.storage.UserStorageProvider"]
    ):
        if item["name"] == "skylus-ldap":
            # domain dc
            domain_dc = f"dc={domain_name},dc=com"

            # set domain
            realm_json["components"]["org.keycloak.storage.UserStorageProvider"][
                db_ind
            ]["config"]["usersDn"] = [f"ou=people,{domain_dc}"]

            # user creds for binding
            # set ldap user for
            realm_json["components"]["org.keycloak.storage.UserStorageProvider"][
                db_ind
            ]["config"]["bindDn"] = [f"cn={ldap_user_name},{domain_dc}"]

            # set password
            realm_json["components"]["org.keycloak.storage.UserStorageProvider"][
                db_ind
            ]["config"]["bindCredential"] = [ldap_user_password]

    # return formatted json
    return realm_json


def create_a_new_realm(
    domain_name: str,
    ldap_user_name: str,
    ldap_user_password: str,
):
    """
    Creates a new realm (domain in openstack)
    """
    try:
        # keycloak admin
        keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username="admin",
            password="admin",
            user_realm_name="master",
            realm_name="skylus",
        )

        # calls export function
        template_realm_json = keycloak_admin.export_realm(
            export_clients=True,
            export_groups_and_role=True,
        )

        # calls realm json
        realm_data = format_realm_json(
            realm_json=template_realm_json,
            ldap_user_name=ldap_user_name,
            ldap_user_password=ldap_user_password,
            domain_name=domain_name,
        )

        # upload to domain.json to keycloak server
        keycloak_admin.import_realm(
            payload=realm_data,
        )

        # return success
        return JSONResponse(
            content={
                "message": f"{domain_name} created successfully!",
            },
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
