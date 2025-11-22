"""
FastAPI Dependencies
Provides reusable dependencies for authentication and authorization
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_access_token
from app.services.auth_service import AuthService
from app.models.user import User


# HTTP Bearer token scheme
# This tells FastAPI to look for "Authorization: Bearer <token>" header
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    This dependency will:
    1. Extract JWT token from Authorization header
    2. Decode and verify the token
    3. Get user from database
    4. Return user object
    
    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session
    
    Returns:
        User: Current authenticated user
    
    Raises:
        HTTPException 401: If token is invalid or user not found
    
    Usage in route:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    # Get token from credentials
    token = credentials.credentials
    
    # Decode token
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get username from token
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database
    user = AuthService.get_user_by_username(db, username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    Additional check to ensure user is active
    
    Args:
        current_user: User from get_current_user
    
    Returns:
        User: Current active user
    
    Raises:
        HTTPException 403: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current superuser (admin)
    Requires user to have superuser privileges
    
    Args:
        current_user: User from get_current_user
    
    Returns:
        User: Current superuser
    
    Raises:
        HTTPException 403: If user is not a superuser
    
    Usage:
        @app.delete("/users/{user_id}")
        async def delete_user(
            user_id: int,
            admin: User = Depends(get_current_superuser)
        ):
            # Only admins can access this
            pass
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Superuser access required."
        )
    return current_user


async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    Useful for endpoints that work both with and without authentication
    
    Args:
        authorization: Authorization header (optional)
        db: Database session
    
    Returns:
        User or None
    
    Usage:
        @app.get("/public")
        async def public_route(user: Optional[User] = Depends(get_optional_user)):
            if user:
                return {"message": f"Hello {user.username}"}
            return {"message": "Hello guest"}
    """
    if not authorization:
        return None
    
    # Check if it's a Bearer token
    if not authorization.startswith("Bearer "):
        return None
    
    # Extract token
    token = authorization.replace("Bearer ", "")
    
    try:
        # Decode token
        payload = decode_access_token(token)
        if payload is None:
            return None
        
        # Get username
        username = payload.get("sub")
        if username is None:
            return None
        
        # Get user
        user = AuthService.get_user_by_username(db, username)
        return user
    
    except Exception:
        return None


def verify_user_owns_resource(
    resource_user_id: int,
    current_user: User
) -> bool:
    """
    Verify that current user owns a resource
    
    Args:
        resource_user_id: User ID associated with resource
        current_user: Current authenticated user
    
    Returns:
        True if user owns resource or is superuser
    
    Raises:
        HTTPException 403: If user doesn't own resource
    
    Usage:
        event = get_event_by_id(event_id)
        verify_user_owns_resource(event.user_id, current_user)
    """
    # Superusers can access any resource
    if current_user.is_superuser:
        return True
    
    # Check if user owns the resource
    if resource_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    
    return True
