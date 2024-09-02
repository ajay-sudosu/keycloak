from fastapi import APIRouter, Depends
from fastapi.requests import Request
from typing import Annotated

from helpers.keycloak_helpers_1 import check_for_resource_permission_4

router = APIRouter(
    prefix="/juju",
    tags=["Juju Service"],
)


@router.get("/juju-service")
def juju_service_list(
    request: Request,
    check_permission: Annotated[dict, Depends(check_for_resource_permission_4)],
):
    """
    Juju Service List API
    """
    return "Juju service list"


@router.get("/juju-service/{juju_service_id}")
def juju_service_detail(
    check_permission: Annotated[dict, Depends(check_for_resource_permission_4)],
    request: Request,
):
    """
    Juju Service Detail API
    """
    return "Juju service detail"
