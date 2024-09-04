def create_user(username, password):
    user_payload = {
        "username": username,
        "enabled": True,
        "emailVerified": True
    }
    return user_payload