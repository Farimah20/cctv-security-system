"""
Authentication service
Business logic for user registration, login, and password reset
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_password_reset_token
)
from app.schemas.user import UserCreate, UserLogin


class AuthService:
    """
    Authentication service class
    Handles all authentication-related operations
    """
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Register a new user
        
        Steps:
        1. Check if username/email already exists
        2. Hash the password
        3. Create new user in database
        4. Return created user
        
        Args:
            db: Database session
            user_data: User registration data
        
        Returns:
            User: Created user object
        
        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username already exists
        existing_user = db.query(User).filter(
            User.username == user_data.username
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create new user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False
        )
        
        # Add to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Optional[User]:
        """
        Authenticate user with username/email and password
        
        Args:
            db: Database session
            login_data: Login credentials
        
        Returns:
            User: User object if authentication successful, None otherwise
        """
        # Find user by username or email
        user = db.query(User).filter(
            (User.username == login_data.username) |
            (User.email == login_data.username)
        ).first()
        
        # If user not found or password doesn't match
        if not user or not verify_password(login_data.password, user.hashed_password):
            return None
        
        # Check if account is active
        if not user.is_active:
            return None
        
        return user
    
    
    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """
        Create JWT access token for user
        
        Args:
            user: User object
        
        Returns:
            str: JWT access token
        """
        # Create token with user information
        token_data = {
            "sub": user.username,  # Subject: username
            "user_id": user.id,     # User ID
            "email": user.email     # Email
        }
        
        return create_access_token(data=token_data)
    
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            db: Database session
            username: Username to search
        
        Returns:
            User: User object if found, None otherwise
        """
        return db.query(User).filter(User.username == username).first()
    
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            db: Database session
            email: Email to search
        
        Returns:
            User: User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
    
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            User: User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()
    
    
    @staticmethod
    def request_password_reset(db: Session, email: str) -> str:
        """
        Create password reset token for user
        
        Steps:
        1. Find user by email
        2. Invalidate any existing reset tokens
        3. Generate new unique token
        4. Save token to database
        5. Return token (to be sent via email)
        
        Args:
            db: Database session
            email: User's email address
        
        Returns:
            str: Reset token
        
        Raises:
            HTTPException: If email not found
        """
        # Find user
        user = AuthService.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        # Invalidate existing tokens for this user
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used == False
        ).update({"is_used": True})
        
        # Generate new token
        token_string = str(uuid.uuid4())
        
        # Create reset token record
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token_string,
            expires_at=datetime.now() + timedelta(minutes=30),
            is_used=False
        )
        
        db.add(reset_token)
        db.commit()
        
        return token_string
    
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """
        Reset user password with token
        
        Steps:
        1. Find token in database
        2. Validate token (not used, not expired)
        3. Hash new password
        4. Update user password
        5. Mark token as used
        
        Args:
            db: Database session
            token: Reset token from email
            new_password: New password
        
        Returns:
            bool: True if successful
        
        Raises:
            HTTPException: If token invalid or expired
        """
        # Find token
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
        
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Check if token is valid
        if not reset_token.is_valid():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired or already been used"
            )
        
        # Get user
        user = AuthService.get_user_by_id(db, reset_token.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash new password
        hashed_password = get_password_hash(new_password)
        
        # Update user password
        user.hashed_password = hashed_password
        user.updated_at = datetime.now()
        
        # Mark token as used
        reset_token.mark_as_used()
        
        # Commit changes
        db.commit()
        
        return True
