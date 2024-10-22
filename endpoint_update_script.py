from keycloak import KeycloakAdmin

keycloak_admin = KeycloakAdmin(
    server_url="http://10.201.11.116:30446",
    username="admin",
    password="admin",
    user_realm_name="master",
    realm_name="netweb",
)



req_list = [
    {
        "resource_name": "/api/v1/compute/hpc/",
        "scope_name": "POST",
        "policy_name": "server-write",
        "permission_name": "hpc-linker",
    },
    {
        "resource_name": "/api/v1/compute/server/k8s",
        "scope_name": "POST",
        "policy_name": "server-write",
        "permission_name": "k8s-linker",
    },
    {
        "resource_name": "/api/v1/compute/server/opslag",
        "scope_name": "POST",
        "policy_name": "server-write",
        "permission_name": "opslag-linker",
    },
    {
        "resource_name": "/api/v1/compute/server/tka",
        "scope_name": "POST",
        "policy_name": "server-write",
        "permission_name": "tka-linker",
    }
]
for req_data in req_list:

    # client uuid
    client_uuid = keycloak_admin.get_client_id(
        client_id="compute-service",
    )

    # check for resource
    resource_list = keycloak_admin.get_client_authz_resources(
        client_id=client_uuid,
    )

    # present bool
    present = False

    # check for resource name
    for resource_data in resource_list:
        if resource_data['name'] == req_data['resource_name']:
            resource_info = resource_data
            present = True
            break

    """
    "name":"/api/v1/auth/identity/test","displayName":"/api/v1/auth/identity/test","type":"","icon_uri":"","ownerManagedAccess":false,"uris":["/api/v1/auth/identity/test"],"attributes":{"level":["domain"]},"scopes":[{"id":"0d31aef9-d583-4866-b016-50fb0a5c85d8","name":"GET","iconUri":"","displayName":"GET"}]}
    """

    # resource scope list
    resource_scopes_list = keycloak_admin.get_client_authz_scopes(
        client_id=client_uuid,
    )

    # get resource scope
    for resource_scope_data in resource_scopes_list:
        if resource_scope_data['name'] == req_data['scope_name']:
            resource_scope = resource_scope_data
            break

    # present
    if not present:
        resource_info = keycloak_admin.create_client_authz_resource(
            client_id=client_uuid,
            payload={
                "name": req_data['resource_name'],
                "displayName": req_data['resource_name'],
                "type": "",
                "uris": [req_data['resource_name']],
                "icon_uri": "",
                "ownerManagedAccess": False,
                "scopes": [resource_scope],
                "attributes": {
                    "level": ["domain"],
                }
            },
        )

    # get policy id
    policies_list = keycloak_admin.get_client_authz_policies(
        client_id=client_uuid,
    )

    # policy prensent checker
    policy_present = False

    # check for policy name
    for policy_data in policies_list:
        # check for policy name
        if policy_data['name'] == req_data['policy_name']:
            policy_info = policy_data
            policy_present = True
            break

    if not policy_present:
        # create policy
        policy_info = keycloak_admin.create_client_authz_role_based_policy(
            client_id=client_uuid,
            payload={
                "type": "role",
                "logic": "POSITIVE",
                "decisionStrategy": "UNANIMOUS",
                "name": req_data['policy_name'],
                "roles": [
                    {
                        "id": 'a664f4ff-aca3-4840-ade6-0ffa05c595b8'
                    }
                ]
            }
        )

    # create permission
    mast = keycloak_admin.create_client_authz_scope_permission(
        payload={
            "name": req_data['permission_name'],
            "type": "scope",
            "logic": "POSITIVE",
            "decisionStrategy": "UNANIMOUS",
            "resources": [resource_info['_id']],
            "scopes": [resource_scope['id']],
            "policies": [policy_info['id']],
        },
        client_id=client_uuid,
    )

    print(mast)
