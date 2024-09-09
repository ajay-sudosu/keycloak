MASTER_REALM_NAME = "master"
REALM_NAME = "temp-realm"
SERVER_URL = "http://localhost:8080"
ADMIN_USER_NAME = "admin"
ADMIN_PASSWORD = "admin"
USER_LOGIN_CLIENT_ID = "user-login"
PROJECT_RESOURCE_ATTRIBUTE_VALUE = "PROJECT"
TOKEN_GENERATE_API_URL = (
    "http://localhost:8000/user/auth/callback"  # REGISTER IN USER_LOGIN_CLIENT
)

# service registered
REGISTERED_SERVICES = [
    "compute-service",
    "storage-service",
    "network-service",
    "juju-service",
    "user-login",  # client for user login token generation
]

# name of template realm
TEMPLATE_REALM_WITH_LDAP = "template-realm"

# microsoft test-sso-creds
MICROSOFT_CLIENT_SECRET = "7~_8Q~w~-uZK3AeYCSdaHO6fzGIIFQDhS_r2fcLt"
