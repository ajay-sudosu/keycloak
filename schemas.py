from pydantic import BaseModel
from enum import Enum
from typing import Optional, List


class UserLogin(BaseModel):
    username: str
    password: str
    domain_name: str


class User(UserLogin):
    email: Optional[str] = None


class Scope(Enum):
    list = "list"
    detail = "detail"


class DomainInput(BaseModel):
    domainName: str
    office_365_custom_logic: bool


class LDAPConfig(BaseModel):
    connectionUrl: List[str]
    # priority: List[str]
    usersDn: List[str]
    uuidLDAPAttribute: List[str]
    bindCredential: List[str]
    bindDn: List[str]
    userObjectClasses: List[str]
    rdnLDAPAttribute: List[str]
    startTls: List[bool]
    usernameLDAPAttribute: List[str]
    connectionPooling: List[bool] = [False, ]
    enabled: List[bool] = [True, ]
    pagination: List[bool] = [False, ]
    fullSyncPeriod: List[str] = ["5", ]
    changedSyncPeriod: List[str] = ["5", ]
    cachePolicy: List[str] = ["DEFAULT", ]
    useKerberosForPasswordAuthentication: List[bool] = [False, ]
    importEnabled: List[bool] = [True, ]
    readTimeout: List[str] = ["10000000", ]
    editMode: List[str] = ["WRITABLE"]
    vendor: List[str] = ['other', ]
    authType: List[str] = ["simple", ]
    krbPrincipalAttribute: List[str] = ["krb5PrincipalName", ]
    searchScope: List[str] = ["1", ]
    useTruststoreSpi: List[str] = ["never", ]
    usePasswordModifyExtendedOp: List[bool] = [False, ]
    trustEmail: List[bool] = [True, ]
    validatePasswordPolicy: List[bool] = [False, ]


class LDAP(BaseModel):
    name: str
    providerId: str
    providerType: str = "org.keycloak.storage.UserStorageProvider"
    config: LDAPConfig


class ADConfig(LDAPConfig):
    vendor: List[str] = ['ad', ]


class AD(LDAP):
    config: ADConfig

