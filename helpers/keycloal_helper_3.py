from keycloak import KeycloakAdmin
from fastapi import HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse

from constants import env


def create_user(username: str, password: str):
    """
    Creates a new user
    """
    try:
        # todo: get the variables from the env file
        # keycloak admin
        keycloak_admin = KeycloakAdmin(
            server_url=env.SERVER_URL,
            username="admin",
            password="admin",
            user_realm_name="master",
            realm_name="skylus",
        )
        user_payload = {
            "username": username,
            "enabled": True,
            "emailVerified": True
        }
        # calls export function
        user_id = keycloak_admin.create_user(
            exist_ok=False,
            payload=user_payload,
        )
        keycloak_admin.set_user_password(user_id, temporary=False, password=password)
        # return success
        return JSONResponse(
            content={
                "message": f"{username} created successfully!",
            },
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
