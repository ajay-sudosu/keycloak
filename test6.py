import json

payload_api_data = {
    "id": "d15c6e96-894e-4980-aa95-d8f5c16ec164",
    "name": "server-read-1",
    "description": "",
    "type": "role",
    "logic": "POSITIVE",
    "decisionStrategy": "UNANIMOUS",
    "config": {
        "fetchRoles": "true",
        "roles": '[{"id":"d803a92b-02ba-4956-995a-40519bb85d76","required":false},{"id":"341cad08-45f2-41e1-96f3-b869291b2cb2","required":false},{"id":"78b28371-0de5-46c4-be32-bcb6206f8083","required":false},{"id":"2547369d-6ee6-48e8-94c9-4074885bec00","required":false},{"id":"44fafccd-0786-487b-8149-f4539f4c48cc","required":false},{"id":"f9c5785b-2529-456b-887d-00ba8ab3b66a","required":false}]',
    },
}


update_payload = payload_api_data

update_payload["fetchRoles"] = payload_api_data["config"].get("fetchRoles")

update_payload["roles"] = json.loads(payload_api_data["config"].get("roles"))

update_payload.pop('config')

update_payload["policies"] = []

print(json.dumps(update_payload))
