import re
import json
import uuid

from keycloak import (
    KeycloakOpenID,
    KeycloakAdmin,
)
from keycloak import (
    uma_permissions,
    KeycloakInvalidTokenError,
    KeycloakAuthenticationError,
)
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from constants import env


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def replace_uuid_with_asterisk(endpoint: str):
    endpoint_components = endpoint.split("/")
    for i, component in enumerate(endpoint_components):
        if is_valid_uuid(component):
            endpoint_components[i] = "*"

    return "/".join(endpoint_components)


def check_project_role_have_access_to_policy(
    resource_name: str,
    resource_scope: str,
    role_uuid: str,
    client_uuid: str,
    domain_name: str,
):
    # keycloak admin obj
    keycloak_admin = KeycloakAdmin(
        username=env.ADMIN_USER_NAME,
        password=env.ADMIN_PASSWORD,
        realm_name=domain_name,
        user_realm_name=env.MASTER_REALM_NAME,
        server_url=env.SERVER_URL,
    )

    # get permissions
    all_permissions = keycloak_admin.get_client_authz_permissions(
        client_id=client_uuid,
    )

    # check for permission
    for permission_data in all_permissions:
        # get resources of permission
        permission_resources = keycloak_admin.get_client_authz_policy_resources(
            client_id=client_uuid,
            policy_id=permission_data["id"],
        )

        # check for matching resource
        for resource_data in permission_resources:
            if resource_data["name"] == resource_name:
                # get all scopes based on permission
                permission_scopes = keycloak_admin.get_client_authz_policy_scopes(
                    client_id=client_uuid,
                    policy_id=permission_data["id"],
                )

                # match the scopes
                for scope_data in permission_scopes:
                    if scope_data["name"] == resource_scope:
                        # permission policy list data
                        permission_policy_list_data = keycloak_admin.get_client_authz_permission_associated_policies(
                            client_id=client_uuid,
                            policy_id=permission_data["id"],
                        )

                        # basic policy data from permission
                        policy_data = permission_policy_list_data[0]

                        # policy detail
                        policy_data = keycloak_admin.get_client_authz_policy(
                            client_id=client_uuid,
                            policy_id=policy_data["id"],
                        )

                        # roles of policy
                        policy_roles_list = json.loads(policy_data["config"]["roles"])

                        # check project role in policy roles
                        for policy_role in policy_roles_list:
                            if role_uuid == policy_role["id"]:
                                return True

    # return false
    return False


def check_for_user_access_to_project_and_resource(
    resource_name: str,
    resource_scope: str,
    username: str,
    client_uuid: str,
    project_id: str,
    domain_name: str,
):
    """
    Check for user access to project and resource
    """
    # check if user have access to project
    # keycloak admin obj
    keycloak_admin = KeycloakAdmin(
        username=env.ADMIN_USER_NAME,
        password=env.ADMIN_PASSWORD,
        realm_name=domain_name,
        user_realm_name=env.MASTER_REALM_NAME,
        server_url=env.SERVER_URL,
    )

    # get user_id
    user_id = keycloak_admin.get_user_id(
        username=username,
    )

    # get user groups
    user_groups = keycloak_admin.get_user_groups(
        user_id=user_id,
    )

    # check for project-access
    for project_data in user_groups:
        if re.search(rf"^/projects/{project_id}", project_data["path"]):
            # fetch the project role
            project_role_data = keycloak_admin.get_group_realm_roles(
                group_id=project_data["id"],
            )

            # project role id
            project_role_id = project_role_data[0]["id"]

            # check the same for resource access
            access_response = check_project_role_have_access_to_policy(
                resource_name=resource_name,
                resource_scope=resource_scope,
                role_uuid=project_role_id,
                client_uuid=client_uuid,
                domain_name=domain_name,
            )

            # raise exp for access denial
            if not access_response:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User is not permitted to access this project!",
                )


def get_username_from_token(
    bearer_token: str,
    domain_name: str,
    service_name: str,
    client_secret_key: str,
):
    # keycloak open id obj
    keycloak_openid = KeycloakOpenID(
        server_url=env.SERVER_URL,
        realm_name=domain_name,
        client_id=service_name,
        client_secret_key=client_secret_key,
    )

    # get userinfo
    try:
        userinfo = keycloak_openid.userinfo(
            token=bearer_token,
        )
        print(userinfo)
    except KeycloakInvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token!",
        )


def check_for_resource_permission(
    request: Request,
):
    try:

        # remove bearer
        if "Authorization" in request.headers:
            bearer_token = request.headers.get("Authorization").replace(
                "Bearer ", ""
            )  # noqa: E501
            endpoint = request.url.path
            print(endpoint)
        else:
            raise RequestValidationError("Token Missing!")

        # fetch the domain_name
        domain_name = request.headers.get("domain_name", None)

        # service name
        service_name = request.headers.get("service_name", None)

        # keycloak admin obj
        keycloak_admin = KeycloakAdmin(
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            realm_name=domain_name,
            user_realm_name=env.MASTER_REALM_NAME,
            server_url=env.SERVER_URL,
        )

        # fetch the project_id
        project_id = request.headers.get("project_id", None)

        # check and replace uuid's with *'s
        endpoint = replace_uuid_with_asterisk(
            endpoint=endpoint,
        )

        # get client id
        client_uuid = keycloak_admin.get_client_id(
            client_id=service_name,
        )

        # get client secret key
        client_secret_key = keycloak_admin.get_client_secrets(
            client_id=client_uuid,
        )

        # get username
        get_username_from_token(
            bearer_token=bearer_token,
            domain_name=domain_name,
            service_name=service_name,
            client_secret_key=client_secret_key,
        )
        username = "jaswanth"

        # if policy is project-based
        if not project_id:

            # keycloak client conn.
            keycloak_openid = KeycloakOpenID(
                server_url=env.SERVER_URL,
                realm_name=domain_name,
                client_id=service_name,
                client_secret_key=client_secret_key,
            )

            keycloak_uma_resource = uma_permissions.Resource(endpoint)
            keycloak_uma_scope = uma_permissions.Scope(request.method)
            keycloak_uma_permission = keycloak_uma_resource(keycloak_uma_scope)

            auth_data = keycloak_openid.has_uma_access(
                token=bearer_token,
                permissions=[keycloak_uma_permission],
            )

            if not auth_data.is_logged_in:
                raise KeycloakInvalidTokenError("Token is Invalid!")
            if not auth_data.is_authorized:
                raise KeycloakAuthenticationError("User is not permitted!")

        else:
            # check with permission with custom logic
            check_for_user_access_to_project_and_resource(
                resource_name=endpoint,
                resource_scope=request.method,
                client_uuid=client_uuid,
                project_id=project_id,
                domain_name=domain_name,
                username=username,
            )

    except KeycloakInvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token!",
        )
    except Exception as e:
        # raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def get_access_token(
    username: str,
    password: str,
    domain_name: str,
):
    try:
        # keycloak admin obj
        keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            user_realm_name=env.MASTER_REALM_NAME,
            realm_name=domain_name,
        )

        # get client id
        client_uuid = keycloak_admin.get_client_id(
            client_id=env.USER_LOGIN_CLIENT_ID,
        )

        # get client secret key
        client_secret_key = keycloak_admin.get_client_secrets(
            client_id=client_uuid,
        )

        # Configuration
        keycloak_openid = KeycloakOpenID(
            server_url=env.SERVER_URL,
            realm_name=domain_name,
            client_id=env.USER_LOGIN_CLIENT_ID,
            client_secret_key=client_secret_key,
        )

        # Obtain token
        token = keycloak_openid.token(
            username=username,
            password=password,
        )

        # Extract the access token
        access_token = token["access_token"]

        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "access_token": access_token,
                "refresh_token": token["refresh_token"],
            },
        )
    except KeycloakAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials!",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def refresh_token(
    request: Request,
    domain_name: str,
):
    try:
        # keycloak admin obj
        keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            user_realm_name=env.MASTER_REALM_NAME,
            realm_name=domain_name,
        )

        # get client id
        client_uuid = keycloak_admin.get_client_id(
            client_id=env.USER_LOGIN_CLIENT_ID,
        )

        # get client secret key
        client_secret_key = keycloak_admin.get_client_secrets(
            client_id=client_uuid,
        )

        # Configuration
        keycloak_openid = KeycloakOpenID(
            server_url=env.SERVER_URL,
            realm_name=domain_name,
            client_id=env.USER_LOGIN_CLIENT_ID,
            client_secret_key=client_secret_key,
        )

        # return refresh token
        refresh_token_resp = keycloak_openid.refresh_token(
            refresh_token=request.headers.get("Authorization").replace(
                "Bearer ",
                "",
            ),  # noqa: E501
            grant_type=["refresh_token"],
        )

        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "access_token": refresh_token_resp["access_token"],
                "refresh_token": refresh_token_resp["refresh_token"],
            },
        )
    except Exception as e:
        # return httpexc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def logout_user(
    request: Request,
    domain_name: str,
):
    try:
        # keycloak admin obj
        keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            user_realm_name=env.MASTER_REALM_NAME,
            realm_name=domain_name,
        )

        # get client id
        client_uuid = keycloak_admin.get_client_id(
            client_id=env.USER_LOGIN_CLIENT_ID,
        )

        # get client secret key
        client_secret_key = keycloak_admin.get_client_secrets(
            client_id=client_uuid,
        )

        # keycloak client conn.
        keycloak_openid = KeycloakOpenID(
            server_url=env.SERVER_URL,
            realm_name=env.REALM_NAME,
            client_id=env.USER_LOGIN_CLIENT_ID,
            client_secret_key=client_secret_key,
        )

        # logout user
        keycloak_openid.logout(
            refresh_token=request.headers.get("Authorization").replace(
                "Bearer ", ""
            )  # noqa: E501
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "detail": "user logged out successfully!",
            },
        )
    except Exception as e:
        # return httpexc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def get_user_info(
    request: Request,
    domain_name: str,
):
    try:
        # keycloak admin obj
        keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            user_realm_name=env.MASTER_REALM_NAME,
            realm_name=domain_name,
        )

        # get client id
        client_uuid = keycloak_admin.get_client_id(
            client_id=env.USER_LOGIN_CLIENT_ID,
        )

        # get client secret key
        client_secret_key = keycloak_admin.get_client_secrets(
            client_id=client_uuid,
        )

        # keycloak client conn.
        keycloak_openid = KeycloakOpenID(
            server_url=env.SERVER_URL,
            realm_name=env.REALM_NAME,
            client_id=env.USER_LOGIN_CLIENT_ID,
            client_secret_key=client_secret_key,
        )

        # get user info
        user = keycloak_openid.userinfo(
            token=request.headers.get("Authorization").replace("Bearer ", "")
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=user,
        )
    except Exception as e:
        # return httpexc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
