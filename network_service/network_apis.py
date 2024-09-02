from fastapi import APIRouter, Depends
from fastapi.requests import Request
from typing import Annotated


from helpers.keycloak_helpers_1 import check_for_resource_permission_3

router = APIRouter(
    prefix="/manage-network",
    tags=["Network"],
)


@router.get("/network")
def network_list(
    request: Request,
    check_permission: Annotated[dict, Depends(check_for_resource_permission_3)],
):
    """
    Network List API
    """
    return "Network list"


@router.get("/network/{network_id}")
def network_detail(
    check_permission: Annotated[dict, Depends(check_for_resource_permission_3)],
    request: Request,
):
    """
    Network Detail API
    """
    return "Network detail"
