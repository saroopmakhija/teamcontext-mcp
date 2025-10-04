import bcrypt
import secrets
import string

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def generate_api_key() -> str:
    """Generate a secure random API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def hash_api_key(api_key: str) -> str:
    """Hash an API key using bcrypt"""
    api_key_bytes = api_key.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(api_key_bytes, salt)
    return hashed.decode('utf-8')

def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Verify an API key against a hash"""
    api_key_bytes = plain_api_key.encode('utf-8')
    hashed_bytes = hashed_api_key.encode('utf-8')
    return bcrypt.checkpw(api_key_bytes, hashed_bytes)
