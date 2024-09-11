from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Serialize private key
pem_private_key = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(b'mypassword')
)

# Generate public key
public_key = private_key.public_key()

# Serialize public key
pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Save to files
with open('/home/ajay-netweb/Documents/skylus/private_key.pem', 'wb') as f:
    f.write(pem_private_key)

with open('/home/ajay-netweb/Documents/skylus/public_key.pem', 'wb') as f:
    f.write(pem_public_key)
