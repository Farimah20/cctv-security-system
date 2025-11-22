"""
Authentication API endpoints
Handles user registration, login, and password reset
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.database import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    PasswordResetRequest,
    PasswordResetConfirm
)
from app.services.auth_service import AuthService

# Create API router
# All routes will be prefixed with /auth
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account
    
    **Request Body:**
    - username: Unique username (3-50 characters)
    - email: Valid email address
    - password: Strong password (min 8 chars, uppercase, lowercase, digit)
    
    **Returns:**
    - User information (without password)
    
    **Errors:**
    - 400: Username or email already exists
    - 422: Invalid data format
    """
    try:
        # Create new user
        new_user = AuthService.register_user(db, user_data)
        
        return new_user
    
    except HTTPException:
        # Re-raise HTTP exceptions (like duplicate username)
        raise
    except Exception as e:
        # Catch any other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with username/email and password
    
    **Request Body:**
    - username: Username or email address
    - password: User password
    
    **Returns:**
    - access_token: JWT token for authentication
    - token_type: "bearer"
    
    **How to use token:**
    Include in request headers:
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Errors:**
    - 401: Invalid credentials or account disabled
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create access token
    access_token = AuthService.create_access_token_for_user(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/password-reset/request")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset
    Generates reset token and sends email (email sending not implemented yet)
    
    **Request Body:**
    - email: Registered email address
    
    **Returns:**
    - message: Success message
    - token: Reset token (in production, this would be sent via email)
    
    **Note:** 
    In production, the token should ONLY be sent via email, not in response.
    For development/testing, we return it in the response.
    
    **Errors:**
    - 404: Email not found
    """
    try:
        # Generate reset token
        token = AuthService.request_password_reset(db, reset_request.email)
        
        # TODO: Send email with reset link
        # send_password_reset_email(reset_request.email, token)
        
        return {
            "message": "Password reset email sent successfully",
            "token": token  # Remove this in production!
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process password reset request: {str(e)}"
        )


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token
    
    **Request Body:**
    - token: Reset token from email
    - new_password: New strong password
    
    **Returns:**
    - message: Success message
    
    **Errors:**
    - 400: Invalid or expired token
    - 404: User not found
    """
    try:
        # Reset password
        success = AuthService.reset_password(
            db,
            reset_confirm.token,
            reset_confirm.new_password
        )
        
        if success:
            return {
                "message": "Password reset successful. You can now login with your new password."
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: Session = Depends(get_db),
    # TODO: Add authentication dependency here
    # current_user: User = Depends(get_current_user_dependency)
):
    """
    Get current authenticated user information
    
    **Requires:** Valid JWT token in Authorization header
    
    **Returns:**
    - Current user information
    
    **Note:** 
    Authentication middleware not yet implemented.
    This endpoint will be completed in next phase.
    """
    # This will be implemented with authentication dependency
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication middleware not yet implemented"
    )


# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Simple health check endpoint
    Tests if authentication API is running
    
    **Returns:**
    - status: "ok"
    """
    return {"status": "ok", "service": "authentication"}
