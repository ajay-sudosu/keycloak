from fastapi import APIRouter
from fastapi.requests import Request

from helpers.keycloak_helpers_1 import (
    get_access_token,
    refresh_token,
    logout_user,
    get_user_info,
    generate_access_token,
    keycloak_signin_page_redirect,
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
        domain_name=request.domain_name,
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
        domain_name=request.query_params.get("domain_name", None),
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


@router.get("/login/new")
def login_microsoft(
    request: Request,
):
    return keycloak_signin_page_redirect(
        request=request,
        domain_name="jasu",
    )


@router.get("/auth/callback")
def call_back_api(
    request: Request,
):
    return generate_access_token(
        request=request,
    )
