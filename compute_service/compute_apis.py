from fastapi import APIRouter, Depends
from fastapi.requests import Request
from typing import Annotated

from helpers.keycloak_helpers_1 import check_for_resource_permission

router = APIRouter(
    prefix="/compute",
    tags=["Compute"],
)


@router.get("/server")
def server_list(
    request: Request,
    check_permission: Annotated[dict, Depends(check_for_resource_permission)],
):
    """
    Server List API
    """
    return "Server list fetched successfully."


@router.get("/server/{server_id}")
def server_detail(
    check_permission: Annotated[dict, Depends(check_for_resource_permission)],
    request: Request,
):
    """
    SERVER Detail API
    """
    return "Server detail"


@router.post("/server")
def server_create(
    check_permission: Annotated[dict, Depends(check_for_resource_permission)],
    request: Request,
):
    """
    Create Server API
    """
    return "Server Created successfully"
