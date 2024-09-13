import base64
import re
import json
import uuid

import random
import string

from keycloak import (
    KeycloakOpenID,
    KeycloakAdmin,
)
from keycloak import (
    uma_permissions,
    KeycloakInvalidTokenError,
    KeycloakAuthenticationError,
)
from keycloak.exceptions import (
    KeycloakOperationError,
)
from modules.microsoft_login import MicrosoftLogin
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse

from constants import env
from db import insert_user


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
    raise KeycloakAuthenticationError(
        "User role is not permitted to access this endpoint!"
    )


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
            return check_project_role_have_access_to_policy(
                resource_name=resource_name,
                resource_scope=resource_scope,
                role_uuid=project_role_id,
                client_uuid=client_uuid,
                domain_name=domain_name,
            )

    raise KeycloakAuthenticationError("User doesn't have access to this project!")


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
    try:
        # get user info
        userinfo = keycloak_openid.userinfo(
            token=bearer_token,
        )

        return userinfo["preferred_username"]
    except KeycloakAuthenticationError:
        raise KeycloakAuthenticationError("Token Expired or Invalid Token!")


def check_for_project_level(
    resource_name: str,
    client_uuid: str,
    domain_name: str,
):
    """
    Checks for PROJECT/DOMAIN in the resource attribute
    """
    # keycloak admin obj
    keycloak_admin = KeycloakAdmin(
        server_url=env.SERVER_URL,
        username=env.ADMIN_USER_NAME,
        password=env.ADMIN_PASSWORD,
        realm_name=domain_name,
        user_realm_name=env.MASTER_REALM_NAME,
    )

    # get all resources
    all_resources_data = keycloak_admin.get_client_authz_resources(
        client_id=client_uuid,
    )

    # get all resources
    for resource_data in all_resources_data:
        if resource_data["name"] == resource_name:
            if resource_data["attributes"]["level"] == [
                env.PROJECT_RESOURCE_ATTRIBUTE_VALUE
            ]:
                return True
            else:
                return False

    return False


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
        else:
            raise RequestValidationError("Token Missing!")

        # fetch the domain_name
        domain_name = request.query_params.get("domain_name", None)

        # service name
        service_name = request.query_params.get("service_name", None)

        # keycloak admin obj
        keycloak_admin = KeycloakAdmin(
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            realm_name=domain_name,
            user_realm_name=env.MASTER_REALM_NAME,
            server_url=env.SERVER_URL,
        )

        # fetch the project_id
        project_id = request.query_params.get("project_id", None)

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
        username = get_username_from_token(
            bearer_token=bearer_token,
            domain_name=domain_name,
            service_name=service_name,
            client_secret_key=client_secret_key,
        )

        project_level_access = check_for_project_level(
            resource_name=endpoint,
            client_uuid=client_uuid,
            domain_name=domain_name,
        )

        # if policy is project-based
        if not project_level_access:

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

        elif project_id is None:
            raise RequestValidationError("Please provide project_id!")
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
    except KeycloakAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except RequestValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
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
        client_secret_key_data = keycloak_admin.get_client_secrets(
            client_id=client_uuid,
        )

        # Configuration
        keycloak_openid = KeycloakOpenID(
            server_url=env.SERVER_URL,
            realm_name=domain_name,
            client_id=env.USER_LOGIN_CLIENT_ID,
            client_secret_key=client_secret_key_data["value"],
        )

        # Obtain token
        token = keycloak_openid.token(
            username=username,
            password=password,
        )

        # Extract the access token
        access_token = token["access_token"]
        user_data = keycloak_openid.userinfo(token=access_token)

        # get the openstack token
        from db import select_user
        user = select_user(username=username)
        if user:
            from secure_pass import secure_the_password
            decrypt_pass = secure_the_password.decrypt_password(user_data["o_pass"])
            if user.password == decrypt_pass:
                o_token = "jkjahjksh123jkjdsfllknnsdfmsfdsk+=="

                # return access token + refresh token
                return JSONResponse(
                    status_code=status.HTTP_202_ACCEPTED,
                    content={
                        "access_token": access_token,
                        "o_token": o_token,
                        "refresh_token": token["refresh_token"],
                    },
                )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
              "body": "Login failed."}
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
            client_secret_key=client_secret_key["value"],
        )

        # return refresh token
        refresh_token_resp = keycloak_openid.refresh_token(
            refresh_token=request.headers.get("Authorization").replace(
                "Bearer ",
                "",
            ),  # noqa: E501
            grant_type=["refresh_token"],
        )

        # return JSON response
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
            client_secret_key=client_secret_key["value"],
        )

        # logout user
        keycloak_openid.logout(
            refresh_token=request.headers.get("Authorization").replace(
                "Bearer ", ""
            )  # noqa: E501
        )

        # return response
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
            client_secret_key=client_secret_key["value"],
        )

        # get user info
        user = keycloak_openid.userinfo(
            token=request.headers.get("Authorization").replace("Bearer ", "")
        )

        # return user data response
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


def keycloak_signin_page_redirect(
    request: Request,
    domain_name: str,
):
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

    # Initialize Keycloak client
    keycloak_openid = KeycloakOpenID(
        server_url=env.SERVER_URL,
        client_id=env.USER_LOGIN_CLIENT_ID,
        realm_name=domain_name,
        client_secret_key=client_secret_key["value"],
    )

    # Generate the authorization URL for Microsoft login
    auth_uri = keycloak_openid.auth_url(
        redirect_uri=env.TOKEN_GENERATE_API_URL,
        scope="openid email profile",
    )

    # redirect to user-login
    return RedirectResponse(url=auth_uri)


def generate_access_token(
    request: Request,
):
    try:
        # extract domain name
        domain_name = request.query_params.get("iss").split("/")[-1]

        # microsoft login helper class obj
        microsoft_login = MicrosoftLogin(
            domain_name=domain_name,
        )

        # get client id
        client_uuid = microsoft_login.get_client_uuid(
            client_name=env.USER_LOGIN_CLIENT_ID,
        )

        # get client secret key
        client_secret_key = microsoft_login.get_client_secrets(
            client_uuid=client_uuid,
        )

        # Handle the callback from Keycloak
        code = request.query_params.get("code")

        # Initialize Keycloak client
        keycloak_openid = KeycloakOpenID(
            server_url=env.SERVER_URL,
            client_id=env.USER_LOGIN_CLIENT_ID,
            realm_name=domain_name,
            client_secret_key=client_secret_key["value"],
        )

        # genrate keycloak access token
        token = keycloak_openid.token(
            code=code,
            grant_type=["authorization_code"],
            redirect_uri=env.TOKEN_GENERATE_API_URL,
        )

        # get user info for checking the domain
        user_data = keycloak_openid.userinfo(token=token["access_token"])

        if user_data[
            "email"
        ] is not None and microsoft_login.check_for_user_microsoft_social_login(
            user_uuid=user_data["sub"]
        ):
            # check the email is same as domain
            if microsoft_login.check_email_against_domain_name(
                email=user_data["email"],
                client_uuid=client_uuid,
                role_name=env.USER_LOGIN_CLIENT_ROLE_NAME,
            ):
                # Extract the access token
                access_token = token["access_token"]

                # return all tokens
                return JSONResponse(
                    status_code=status.HTTP_202_ACCEPTED,
                    content={
                        "access_token": access_token,
                        "refresh_token": token["refresh_token"],
                    },
                )
            else:
                # delete user from keycloak
                microsoft_login.delete_user(
                    user_uuid=user_data["sub"],
                )

                # send the invalid domain email error
                raise KeycloakOperationError("Email doesn't belong to this domain!")

        # Extract the access token
        access_token = token["access_token"]

        # return all tokens
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
    except KeycloakOperationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def user_create(username: str, domain_name: str, password: str, email: str = None):
    payload = {"username": username,
               "email": email,
               "enabled": True,}
    from secure_pass import secure_the_password
    try:
        # keycloak admin obj
        keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            user_realm_name=env.MASTER_REALM_NAME,
            realm_name="skylus",
        )
        try:
            # openstack user creation
            skylus_password = generate_random_string()
            user = insert_user(username=username, password=skylus_password, domain_name=domain_name)
            if user:
                #  keycloak user creation
                encrypt_password = secure_the_password.encrypt_password(password=skylus_password)
                # adding the encrypted openstack password
                payload["attributes"] = {"o_pass": encrypt_password}
                user_id = keycloak_admin.create_user(payload=payload, exist_ok=False)
                keycloak_admin.set_user_password(user_id=user_id, password=password, temporary=False)
                return {"message": f"User created- {user_id}"}
            else:
                return {"message": f"User creation failed."}
        except Exception as e:
            return {"msg": str(e)}
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


def generate_random_string(length=16):
    letters = string.ascii_letters  # a-z, A-Z
    return ''.join(random.choice(letters) for _ in range(length))


def add_ldap_configuration(payload: dict, domain_name: str):
    try:
        keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username=env.ADMIN_USER_NAME,
            password=env.ADMIN_PASSWORD,
            user_realm_name=env.MASTER_REALM_NAME,
            realm_name=domain_name,
        )
        storage_id = keycloak_admin.create_component(payload=payload)
        result = keycloak_admin.sync_users(storage_id=storage_id, action="triggerFullSync")
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
