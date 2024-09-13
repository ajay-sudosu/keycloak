from keycloak import KeycloakAdmin
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from constants import env


def remove_ids(data):
    # remove ids from all the fields
    if isinstance(data, dict):
        data.pop("id", None)
        data.pop("_id", None)
        data.pop("internalId", None)
        for key, value in data.items():
            remove_ids(value)
    elif isinstance(data, list):
        for item in data:
            remove_ids(item)

    return data


def format_realm_json(
    realm_json: dict,
    domain_name: str,
    office_365_custom: bool,
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

    # # configure ldap settings
    # for db_ind, item in enumerate(
    #     realm_json["components"]["org.keycloak.storage.UserStorageProvider"]
    # ):
    #     if item["name"] == "skylus-ldap":
    #         # domain dc
    #         domain_dc = f"dc={domain_name},dc=com"

    #         # set domain
    #         realm_json["components"]["org.keycloak.storage.UserStorageProvider"][
    #             db_ind
    #         ]["config"]["usersDn"] = [f"ou=people,{domain_dc}"]

    #         # user creds for binding
    #         # set ldap user for
    #         realm_json["components"]["org.keycloak.storage.UserStorageProvider"][
    #             db_ind
    #         ]["config"]["bindDn"] = [f"cn={ldap_user_name},{domain_dc}"]

    #         # set password
    #         realm_json["components"]["org.keycloak.storage.UserStorageProvider"][
    #             db_ind
    #         ]["config"]["bindCredential"] = [ldap_user_password]

    if office_365_custom:
        # update the realm settings with microsoft client creds
        for i, identity_provider in enumerate(realm_json["identityProviders"]):
            if identity_provider["alias"] == "microsoft":
                realm_json["identityProviders"][i]["config"][
                    "clientSecret"
                ] = env.DOMAIN_LOGIN

        # remove authentication flow
        # realm_json.pop("authenticationFlows", None)

    # return formatted json
    return realm_json


def regenerate_all_registered_service_client_creds(
    domain_name: str,
):
    """
    Regenerates all the registered service client creds
    """
    # keycloak admin obj
    keycloak_admin = KeycloakAdmin(
        server_url=env.SERVER_URL,
        username=env.ADMIN_USER_NAME,
        password=env.ADMIN_PASSWORD,
        user_realm_name=env.MASTER_REALM_NAME,
        realm_name=domain_name,
    )

    # loop through service-names list
    for service in env.REGISTERED_SERVICES:
        # client uuid
        client_uuid = keycloak_admin.get_client_id(
            client_id=service,
        )

        # generate new client secret cred
        keycloak_admin.generate_client_secrets(
            client_id=client_uuid,
        )


def create_a_new_realm_from_raw_template_realm(
    domain_name: str,
):
    """
    Creates a new realm (domain in openstack)
    """
    try:
        # keycloak admin
        keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            user_realm_name=env.MASTER_REALM_NAME,
            realm_name=env.RAW_TEMPLATE_REALM,
        )

        # calls export function
        template_realm_json = keycloak_admin.export_realm(
            export_clients=True,
            export_groups_and_role=True,
        )

        # calls realm json
        realm_data = format_realm_json(
            realm_json=template_realm_json,
            domain_name=domain_name,
            office_365_custom=False,
        )

        # upload to domain.json to keycloak server
        keycloak_admin.import_realm(
            payload=realm_data,
        )

        # regenerate client tokens
        regenerate_all_registered_service_client_creds(
            domain_name=domain_name,
        )

        # TODO: generate domain in openstack

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


def create_a_new_realm_from_office365_custom_logic_template_realm(
    domain_name: str,
):
    """
    Creates a new realm (domain in openstack)
    """
    try:
        # keycloak admin
        keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            user_realm_name=env.MASTER_REALM_NAME,
            realm_name=env.OFFICE_365_CUSTOM_FLOW_TEMPLATE_REALM,
        )

        # calls export function
        template_realm_json = keycloak_admin.export_realm(
            export_clients=True,
            export_groups_and_role=True,
        )

        # calls realm json
        realm_data = format_realm_json(
            realm_json=template_realm_json,
            domain_name=domain_name,
            office_365_custom=True,
        )

        # upload to domain.json to keycloak server
        keycloak_admin.import_realm(
            payload=realm_data,
        )

        # TODO: integrate api that adds uri to microsoft azure app registrations

        # regenerate client tokens
        regenerate_all_registered_service_client_creds(
            domain_name=domain_name,
        )

        # TODO: generate domain in openstack

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
