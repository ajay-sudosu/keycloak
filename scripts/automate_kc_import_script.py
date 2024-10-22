"""
This script create a domain called 'raw-template' and imports all the data from a template called raw-template.json.
It also creates login client 'user-login' in master domain.
Author: XYZ
Date: 2024-10-22
"""

import json
import os.path

from keycloak import KeycloakAdmin
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

# super admin creds

username = "admin"
domain_name = "admin_domain"

# kc configuration
primary_project_name = "primary"
domain_attribute_group = "domain_attribute"
default_internal_role = "admin"
default_role_on_domain = "domain_admin"
default_role_on_project = "project_admin"
primary_project = "primary"
AUTH_SERVER_URL = "http://10.201.11.116:30446"  # change it to kc url ex: http://<ip>:port
AUTH_SERVER_ADMIN_USERNAME = "admin"
AUTH_SERVER_ADMIN_PASSWORD = "admin"
AUTH_SERVER_MASTER_REALM_NAME = "master"
AUTH_SERVER_USER_LOGIN_CLIENT_ID = "user-login"
AUTH_SERVER_RAW_TEMPLATE_NAME = "raw-template"
AUTH_SERVER_REGISTERED_SERVICES = [
    "compute-service",
    "storage-service",
    "network-service",
    "auth-service",
    "billing-service",
    "user-login",
]

# domain level resource attribute name

AUTH_SERVER_DOMAIN_ATTRIBUTE_VALUE = "domain"
# project level resource attribute name
AUTH_SERVER_PROJECT_ATTRIBUTE_VALUE = "project"
IGNORE_TEMPLATES = ["raw-template", "master"]

# keycloak auth service name registered variable

AUTH_SERVER_REGISTERED_SERVICE_NAME = "auth-service"

# default roles

AUTH_SERVER_DEFAULT_ROLE_NAMES = [
    "domain_admin",
    "domain_member",
    "domain_reader",
    "project_admin",
    "project_member",
    "project_reader",
]
REGISTERED_SERVICES = ["COMPUTE", "STORAGE", "NETWORK", "AUTH"]
ROLE_LEVELS = ["project", "domain"]


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


def regenerate_all_registered_service_client_creds(
    domain_name: str,
):
    """
    Regenerates all the registered service client creds
    """
    # keycloak admin obj
    keycloak_admin = KeycloakAdmin(
        server_url=AUTH_SERVER_URL,
        username=AUTH_SERVER_ADMIN_USERNAME,
        password=AUTH_SERVER_ADMIN_PASSWORD,
        user_realm_name=AUTH_SERVER_MASTER_REALM_NAME,
        realm_name=domain_name,
    )

    # auth server registered services
    registered_services = AUTH_SERVER_REGISTERED_SERVICES

    # loop through service-names list
    for service in registered_services:
        # client uuid
        client_uuid = keycloak_admin.get_client_id(
            client_id=service,
        )

        # generate new client secret cred
        keycloak_admin.generate_client_secrets(
            client_id=client_uuid,
        )


def create_user_login_in_master_regenerate_client():
    """Create user-login client in master + regenerate client creds"""
    # keycloak admin obj
    keycloak_admin = KeycloakAdmin(
        server_url=AUTH_SERVER_URL,
        username=AUTH_SERVER_ADMIN_USERNAME,
        password=AUTH_SERVER_ADMIN_PASSWORD,
        realm_name=AUTH_SERVER_MASTER_REALM_NAME,
    )

    # create cleint
    keycloak_admin.create_client(
        payload={
            "protocol": "openid-connect",
            "clientId": AUTH_SERVER_USER_LOGIN_CLIENT_ID,
            "name": AUTH_SERVER_USER_LOGIN_CLIENT_ID,
            "description": "",
            "publicClient": False,
            "authorizationServicesEnabled": True,
            "serviceAccountsEnabled": True,
            "implicitFlowEnabled": False,
            "directAccessGrantsEnabled": True,
            "standardFlowEnabled": True,
            "frontchannelLogout": True,
            "attributes": {
                "saml_idp_initiated_sso_url_name": "",
                "oauth2.device.authorization.grant.enabled": False,
                "oidc.ciba.grant.enabled": False
            },
            "alwaysDisplayInConsole": True,
            "rootUrl": "",
            "baseUrl": ""
        },
        skip_exists=True,
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
            server_url=AUTH_SERVER_URL,
            username=AUTH_SERVER_ADMIN_USERNAME,
            password=AUTH_SERVER_ADMIN_PASSWORD,
            user_realm_name=AUTH_SERVER_MASTER_REALM_NAME,
            realm_name=AUTH_SERVER_RAW_TEMPLATE_NAME,
        )

        #
        with open("raw-template.json", "r", encoding="utf-8") as json_file:
            # extract raw template data
            template_realm_json = json.load(json_file)

        # # calls realm json
        realm_data = format_realm_json(
            realm_json=template_realm_json,
            domain_name=domain_name,
        )

        print(realm_data)

        # upload to domain.json to keycloak server
        keycloak_admin.import_realm(
            payload=realm_data,
        )

        # regenerate client tokens
        regenerate_all_registered_service_client_creds(
            domain_name=domain_name,
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


def create_a_new_realm_template_realm(
    domain_name: str,
):
    """
    Creates a new realm (domain in openstack)
    """
    if not os.path.exists("./raw-template.json"):
        raise FileNotFoundError("'raw-template.json' file not found")

    try:
        # keycloak admin
        keycloak_admin = KeycloakAdmin(
            server_url=AUTH_SERVER_URL,
            username=AUTH_SERVER_ADMIN_USERNAME,
            password=AUTH_SERVER_ADMIN_PASSWORD,
            realm_name=AUTH_SERVER_MASTER_REALM_NAME,
        )

        # import data
        with open("raw-template.json", "r", encoding="utf-8") as json_file:
            template_realm_json = json.load(json_file)

        # calls realm json
        realm_data = format_realm_json(
            realm_json=template_realm_json,
            domain_name=domain_name,
        )

        # upload to domain.json to keycloak server
        keycloak_admin.import_realm(
            payload=realm_data,
        )

        # regenerate client tokens
        regenerate_all_registered_service_client_creds(
            domain_name=domain_name,
        )

        # create user-login in master realm
        create_user_login_in_master_regenerate_client()
        print("*** Template created successfully. ***")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


create_a_new_realm_template_realm(domain_name=AUTH_SERVER_RAW_TEMPLATE_NAME)
# create_a_new_realm_template_realm(domain_name="test_domain")
