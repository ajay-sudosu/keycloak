from fastapi import APIRouter
from fastapi.requests import Request
from schemas import DomainInput


from helpers.keycloak_helpers_2 import (
    create_a_new_realm_from_raw_template_realm,
    create_a_new_realm_from_office365_custom_logic_template_realm,
)


router = APIRouter(
    prefix="/domain",
    tags=["Domain"],
)


@router.post("/create-domain")
def create_domain(
    request: Request,
    domain_create_input: DomainInput,
):
    if domain_create_input.office_365_custom_logic:
        return create_a_new_realm_from_office365_custom_logic_template_realm(
            domain_name=domain_create_input.domainName,
        )
    else:
        return create_a_new_realm_from_raw_template_realm(
            domain_name=domain_create_input.domainName,
        )
