from fastapi import APIRouter
from fastapi.requests import Request
from schemas import DomainInput


from helpers.keycloak_helpers_2 import create_a_new_realm


router = APIRouter(
    prefix="/domain",
    tags=["Domain"],
)


@router.post("/create-domain")
def create_domain(
    request: Request,
    domain_create_input: DomainInput,
):
    return create_a_new_realm(
        domain_name=domain_create_input.domainName,
        ldap_user_name=domain_create_input.ldapUsername,
        ldap_user_password=domain_create_input.ldapPassword,
    )
