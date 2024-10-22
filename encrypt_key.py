from jose import jwe, jwk
import json

# Define your payload
payload = {"o_pass": "akfnakjfnas", "kc_pass": "akfdnfksnasldgjass"}

# Convert payload to JSON format
payload_json = json.dumps(payload)

# Generate a symmetric key (this key must be securely stored)
encryption_key = jwk.construct('your-very-strong-encryption-key')

# Encrypt the JWT using JWE (JSON Web Encryption)
encrypted_token = jwe.encrypt(payload_json.encode(), encryption_key, algorithm='A256KW', encryption='A256CBC-HS512')

print("Encrypted Token:", encrypted_token)


# Decrypt the JWT when needed
decrypted_payload_json = jwe.decrypt(encrypted_token, encryption_key).decode()
decrypted_payload = json.loads(decrypted_payload_json)

print("Decrypted Payload:", decrypted_payload)
