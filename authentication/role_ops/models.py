from typing import List, Optional
from manage_users.roles.models import (
    Parent,
    Create,
    Modify,
    Deleteroles,
    roledata,
    RoleTenant,
    RoleProject,
)
from enum import Enum


class Create(Create):
    tenant_id: Optional[str] = None


class Modify(Modify):
    pass


class roledata(roledata):
    name: str
    id: str


class Deleteroles(Deleteroles):
    tenant_id: Optional[str]


class RoleTenant(RoleTenant):
    tenant_id: Optional[str]


class RoleProject(RoleProject):
    pass

# policy models
class Policy(Parent):
    name: str
    id: str


class AssignPolicy(Parent):
    policy_id: List[Policy]
    policy_level: str


class RoleMapper(Enum):
    DOMAIN = "domain"
    PROJECT = "project"
