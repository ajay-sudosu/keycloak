from fastapi import APIRouter, Depends
from fastapi.requests import Request
from typing import Annotated

from helpers.keycloak_helpers_1 import check_for_resource_permission_1

router = APIRouter(
    prefix="/compute",
    tags=["Compute"],
)


@router.get("/server")
def server_list(
    request: Request,
    check_permission: Annotated[dict, Depends(check_for_resource_permission_1)],
):
    """
    Server List API
    """
    return "Server list"


@router.get("/server/{server_id}")
def server_detail(
    check_permission: Annotated[dict, Depends(check_for_resource_permission_1)],
    request: Request,
):
    """
    SERVER Detail API
    """
    return "Server detail"


@router.post("/server")
def server_create(
    check_permission: Annotated[dict, Depends(check_for_resource_permission_1)],
    request: Request,
):
    """
    Create Server API
    """
    return "Server Create"
