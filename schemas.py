from pydantic import BaseModel
from enum import Enum
from typing import Optional


class UserLogin(BaseModel):
    username: str
    password: Optional[str] = None
    domain_name: str


class User(UserLogin):
    email: str


class Scope(Enum):
    list = "list"
    detail = "detail"


class DomainInput(BaseModel):
    domainName: str
    office_365_custom_logic: bool
