import json

error = b'{"error": "message"}'
print(type(error))

error = error.decode()

error = json.loads(error)