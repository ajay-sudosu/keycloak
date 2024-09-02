from fastapi import APIRouter
from fastapi.requests import Request

from helpers.keycloak_helpers_1 import (
    get_access_token,
    refresh_token,
    logout_user,
    get_user_info,
)

from schemas import User

router = APIRouter(
    prefix="/user",
    tags=["User authentication"],
)


@router.post("/login")
def user_login(
    request: User,
):
    """
    User login API
    """
    return get_access_token(
        username=request.username,
        password=request.password,
    )


@router.post("/refresh-token")
def refresh_token_api(
    request: Request,
):
    """
    User access Refresh Token API
    """
    return refresh_token(
        request=request,
    )


@router.get("/logout")
def user_logout(
    request: Request,
):
    """
    User Logout API
    """
    return logout_user(
        request=request,
    )


@router.get("/info")
def get_user_info_api(
    request: Request,
):
    """
    User info API
    """
    return get_user_info(
        request=request,
    )
