from fastapi import APIRouter
from fastapi.requests import Request

from helpers.keycloak_helpers_1 import (
    get_access_token,
    refresh_token,
    logout_user,
    get_user_info,
    generate_access_token,
    keycloak_signin_page_redirect,
    user_create,
    add_ldap_configuration,
)

from schemas import User, UserLogin, LDAP


router = APIRouter(
    prefix="/user",
    tags=["User authentication"],
)


@router.post("/login")
def user_login(
    request: UserLogin,
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


@router.get("/login/new/{domain_name}")
def login_microsoft(
    request: Request,
    domain_name: str,
):
    return keycloak_signin_page_redirect(
        request=request,
        domain_name=domain_name,
    )


@router.get("/auth/callback")
def call_back_api(
    request: Request,
):
    return generate_access_token(
        request=request,
    )


@router.post("/auth/create")
def user_create_(user_obj: User):
    try:
        user_obj = user_obj.model_dump()
        return user_create(**user_obj)
    except Exception as e:
        return {"msg": str(e)}


@router.post("/configure-LDAP")
def configure_ldap(request: Request, ldap_obj: LDAP):
    try:
        domain_name = request.query_params.get(
            "domain_name",
            None,
        )
        ldap_payload = ldap_obj.model_dump()
        return add_ldap_configuration(ldap_payload, domain_name)
    except Exception as e:
        return {"msg": str(e)}
