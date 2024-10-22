from keycloak import uma_permissions
from authentication.base.openid_base import OpenID


class UmaBase(OpenID):
    """
    Baseclass for KeycloakUma (contains all the keycloak uma methods )
    """

    def __init__(
        self,
        domain_name: str,
        client_name: str,
    ):
        super().__init__(
            domain_name=domain_name,
            client_name=client_name,
        )
        # uma_permissions object
        self.uma_pemissions = uma_permissions

    def resource_obj(
        self,
        resource_endpoint: str,
    ):
        """
        keycloak uma resourc obj
        """
        # return uma resource obj
        return self.uma_pemissions.Resource(
            resource=resource_endpoint,
        )

    def resouce_scope_obj(
        self,
        resource_scope: str,
    ):
        """
        Resource scope uma obj
        """
        # return uma resource scope obj
        return self.uma_pemissions.Scope(
            scope=resource_scope,
        )
