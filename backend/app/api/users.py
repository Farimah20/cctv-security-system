"""
User Management API endpoints
Handles user profile, preferences, and account management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_superuser
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.security import get_password_hash


# Create API router
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile
    
    **Requires:** Valid JWT token in Authorization header
    
    **Returns:**
    - Current user information
    
    **Example:**
    ```
    Authorization: Bearer <your_token>
    ```
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    
    **Requires:** Valid JWT token
    
    **Request Body:**
    - email: New email (optional)
    - username: New username (optional)
    - password: New password (optional)
    
    **Returns:**
    - Updated user information
    
    **Errors:**
    - 400: Username or email already taken
    """
    # Check if username is being changed and is already taken
    if user_update.username and user_update.username != current_user.username:
        existing_user = AuthService.get_user_by_username(db, user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username
    
    # Check if email is being changed and is already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = AuthService.get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
        current_user.email = user_update.email
    
    # Update password if provided
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    # Update is_active if provided (only for self)
    if user_update.is_active is not None:
        current_user.is_active = user_update.is_active
    
    # Save changes
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.delete("/me")
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user's account
    
    **Requires:** Valid JWT token
    
    **Warning:** This action is permanent and will delete all associated data!
    
    **Returns:**
    - Success message
    """
    # Delete user (cascade will delete events, tokens, etc.)
    db.delete(current_user)
    db.commit()
    
    return {
        "message": "Account deleted successfully",
        "username": current_user.username
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (Admin only)
    
    **Requires:** Superuser privileges
    
    **Parameters:**
    - user_id: User ID to retrieve
    
    **Returns:**
    - User information
    
    **Errors:**
    - 403: Not a superuser
    - 404: User not found
    """
    user = AuthService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only)
    
    **Requires:** Superuser privileges
    
    **Parameters:**
    - skip: Number of records to skip
    - limit: Maximum number of records to return
    
    **Returns:**
    - List of users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Delete a user (Admin only)
    
    **Requires:** Superuser privileges
    
    **Parameters:**
    - user_id: User ID to delete
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 403: Not a superuser
    - 404: User not found
    """
    user = AuthService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account. Use /users/me endpoint instead."
        )
    
    db.delete(user)
    db.commit()
    
    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }


# Health check
@router.get("/health/check")
async def users_health_check():
    """
    Health check for users API
    """
    return {
        "status": "ok",
        "service": "users"
    }
