"""
Security utilities for authentication
Handles password hashing, JWT token creation/verification
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings


# Password hashing context
# Uses bcrypt algorithm for secure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    
    Args:
        plain_password: Password entered by user
        hashed_password: Stored hashed password from database
    
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        str: Bcrypt hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    
    JWT Structure:
    - Header: Algorithm and token type
    - Payload: User data (sub, exp, etc.)
    - Signature: Ensures token hasn't been tampered with
    
    Args:
        data: Dictionary containing user information (usually user_id)
        expires_delta: Optional custom expiration time
    
    Returns:
        str: Encoded JWT token
    """
    # Copy data to avoid modifying original
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiration from settings (24 hours)
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Add expiration to token payload
    to_encode.update({"exp": expire})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload if valid, None otherwise
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # Token is invalid or expired
        return None


def create_password_reset_token(email: str) -> str:
    """
    Create a JWT token for password reset
    Shorter expiration time for security (30 minutes)
    
    Args:
        email: User's email address
    
    Returns:
        str: Password reset token
    """
    delta = timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "type": "password_reset"}
    return create_access_token(data=to_encode, expires_delta=delta)


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token and extract email
    
    Args:
        token: Password reset token
    
    Returns:
        str: Email if token is valid, None otherwise
    """
    payload = decode_access_token(token)
    if payload and payload.get("type") == "password_reset":
        return payload.get("sub")  # Returns email
    return None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    
    Requirements:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    
    Args:
        password: Password to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is strong"


# Example usage and testing
if __name__ == "__main__":
    print("🔐 Security Module Test")
    print("=" * 50)
    
    # Test password hashing
    password = "TestPassword123"
    hashed = get_password_hash(password)
    print(f"✅ Password hashed: {hashed[:50]}...")
    
    # Test password verification
    is_valid = verify_password(password, hashed)
    print(f"✅ Password verification: {is_valid}")
    
    # Test JWT token creation
    token = create_access_token(data={"sub": "testuser", "user_id": 1})
    print(f"✅ JWT Token created: {token[:50]}...")
    
    # Test JWT token decoding
    decoded = decode_access_token(token)
    print(f"✅ Token decoded: {decoded}")
    
    # Test password strength validation
    weak_password = "123"
    strong_password = "SecurePass123"
    
    is_strong, msg = validate_password_strength(weak_password)
    print(f"❌ Weak password: {msg}")
    
    is_strong, msg = validate_password_strength(strong_password)
    print(f"✅ Strong password: {msg}")