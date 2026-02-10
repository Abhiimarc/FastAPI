import hashlib
from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
def _prehash_if_needed(password: str) -> str:
    """
    bcrypt only accepts up to 72 bytes.
    If password is longer, pre-hash with SHA-256 to fixed length, then bcrypt.
    """
    b = password.encode("utf-8")
    if len(b) <= 72:
        return password
    return hashlib.sha256(b).hexdigest()

def hash_password(password: str) -> str:
    return pwd_context.hash(_prehash_if_needed(password))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_prehash_if_needed(plain_password), hashed_password)