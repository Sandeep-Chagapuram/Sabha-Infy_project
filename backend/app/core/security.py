from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
import bcrypt
from app.core.config import settings
import re

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')[:72]
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def sanitize_untrusted_input(text: str) -> str:
    """
    Sanitizes untrusted transcript or web input to prevent prompt injection 
    and delimiter spoofing without mangling genuine speaker punctuation.
    """
    if not text:
        return ""
    # Strip dangerous control instructions or pseudo system prompts
    cleaned = re.sub(r'(?i)<\|im_start\|>|<\|im_end\|>|\[SYSTEM\]|\[INSTRUCTION\]', '', text)
    # Normalize excessive null or non-printable chars
    cleaned = ''.join(c for c in cleaned if c.isprintable() or c in '\n\r\t ')
    return cleaned.strip()
