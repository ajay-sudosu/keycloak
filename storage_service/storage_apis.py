from fastapi import APIRouter, Depends
from fastapi.requests import Request
from typing import Annotated

from helpers.keycloak_helpers_1 import check_for_resource_permission

router = APIRouter(
    prefix="/storage",
    tags=["Storage"],
)


@router.get("/volume")
def volume_list(
    request: Request,
    check_permission: Annotated[dict, Depends(check_for_resource_permission)],
):
    """
    Volume List API
    """
    return "Volume list"


@router.get("/volume/{volume_id}")
def volume_detail(
    request: Request,
    check_permission: Annotated[dict, Depends(check_for_resource_permission)],
):
    """
    Volume Detail API
    """
    return "Volume detail"
