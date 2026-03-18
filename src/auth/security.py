import bcrypt

def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed


def verify_password(password: str, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password)