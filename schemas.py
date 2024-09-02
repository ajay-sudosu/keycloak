from pydantic import BaseModel
from enum import Enum


class User(BaseModel):
    username: str
    password: str


class Scope(Enum):
    list = "list"
    detail = "detail"


class DomainInput(BaseModel):
    domainName: str
    ldapUsername: str
    ldapPassword: str
