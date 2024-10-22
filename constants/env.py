MASTER_REALM_NAME = "master"
REALM_NAME = "skylus"
SERVER_URL = "http://localhost:8080"
ADMIN_USER_NAME = "admin"
ADMIN_PASSWORD = "admin"
USER_LOGIN_CLIENT_ID = "user-login"
USER_LOGIN_CLIENT_ROLE_NAME = "attribute-role"
PROJECT_RESOURCE_ATTRIBUTE_VALUE = "PROJECT"
TOKEN_GENERATE_API_URL = (
    "http://localhost:8000/user/auth/callback"  # REGISTER IN USER_LOGIN_CLIENT
)

# service registered
REGISTERED_SERVICES = [
    "compute-service",
    "storage-service",
    "network-service",
    "billing-service",
    "auth-service",
    "user-login",  # client for user login token generation
]

# name of template realm
RAW_TEMPLATE_REALM = "raw-template"
OFFICE_365_CUSTOM_FLOW_TEMPLATE_REALM = "office-365-custom-logic-template"

# microsoft test-sso-creds
MICROSOFT_CLIENT_SECRET = "7~_8Q~w~-uZK3AeYCSdaHO6fzGIIFQDhS_r2fcLt"

MICROSOFT_NEW_CLIENT_SECRET = "t298Q~zLVKTUKXJrbIEwhcDBbvSC56Fkq4EQdcYE"

DOMAIN_LOGIN = "qkF8Q~n-ZrMByddV5SzssOjm4YPGrtsSgpygDcBQ"
