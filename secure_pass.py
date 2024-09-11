from rsa import PublicKey, PrivateKey, encrypt, decrypt
from base64 import b64encode, b64decode



class SecurePassword:
    def encrypt_password(self, password):
        public_key = b'-----BEGIN RSA PUBLIC KEY-----\nMEgCQQCKmaKWnYgHjkAQS8A05WxBX0hvguU82L9BVyUpdDOtiTgdRURLHT/MbQlQ\nZOMRv1OO+jwnNzs7kHMU03pLKdwFAgMBAAE=\n-----END RSA PUBLIC KEY-----\n'
        public_key = PublicKey.load_pkcs1(public_key)
        encrypted_password = encrypt(password.encode(), public_key)
        return b64encode(encrypted_password).decode()

    def decrypt_password(self, encrypted_password):
        # Please add this in config json
        # "private_key_for_secure_password": "-----BEGIN RSA PRIVATE KEY-----\\nMIIBPAIBAAJBAIqZopadiAeOQBBLwDTlbEFfSG+C5TzYv0FXJSl0M62JOB1FREsd\\nP8xtCVBk4xG/U476PCc3OzuQcxTTeksp3AUCAwEAAQJAZd6gIwWsGqmSKqgSoI5T\\nsATBb7yMktlYUUUk+j/+vTSP5g5V21owvU1Ay+GvhptONJ+4FDwwKWJ/ll9MqFGf\\nLQIjAMdXm0zpGBqpp5VKVhUFO15PoHLc72ZZ4EqbWYYGFFXek48CHwCx/luNiOa9\\nxmKWcliL69leV3vdD5JRAtPvfymCPSsCIwDEpCYdq37MpnkbKvZZzAxxj2j+hfVe\\n6N/5mN+p9wtOXb7/Ah5c89l5+4GMn7rCmKp3P86/fu5Xjpc5qUFmtEDIHAsCIgj4\\n44LdTfoXYmG5lSvPCrWl0xw6Yz5JQew8AMmer7VDiBQ=\\n-----END RSA PRIVATE KEY-----\\n",
        private_key = b"-----BEGIN RSA PRIVATE KEY-----\nMIIBPAIBAAJBAIqZopadiAeOQBBLwDTlbEFfSG+C5TzYv0FXJSl0M62JOB1FREsd\nP8xtCVBk4xG/U476PCc3OzuQcxTTeksp3AUCAwEAAQJAZd6gIwWsGqmSKqgSoI5T\nsATBb7yMktlYUUUk+j/+vTSP5g5V21owvU1Ay+GvhptONJ+4FDwwKWJ/ll9MqFGf\nLQIjAMdXm0zpGBqpp5VKVhUFO15PoHLc72ZZ4EqbWYYGFFXek48CHwCx/luNiOa9\nxmKWcliL69leV3vdD5JRAtPvfymCPSsCIwDEpCYdq37MpnkbKvZZzAxxj2j+hfVe\n6N/5mN+p9wtOXb7/Ah5c89l5+4GMn7rCmKp3P86/fu5Xjpc5qUFmtEDIHAsCIgj4\n44LdTfoXYmG5lSvPCrWl0xw6Yz5JQew8AMmer7VDiBQ=\n-----END RSA PRIVATE KEY-----\n"
        private_key = PrivateKey.load_pkcs1(private_key)
        decrypted_message = decrypt(b64decode(encrypted_password.encode()), private_key).decode()
        return decrypted_message

secure = SecurePassword()

a = "netweb"

encrypt_pass = secure.encrypt_password(a)
print(encrypt_pass)
decrypt_pass = secure.decrypt_password(encrypt_pass)
print(decrypt_pass)

