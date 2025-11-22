"""
Pydantic schemas for user-related data validation
These schemas validate incoming/outgoing data in API requests/responses
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Base schema with common user fields
    Used as parent class for other user schemas
    """
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")


class UserCreate(UserBase):
    """
    Schema for user registration
    Includes password field
    """
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength during registration
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate username format
        """
        if not v.replace('_', '').isalnum():
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v


class UserLogin(BaseModel):
    """
    Schema for user login
    Accepts either username or email
    """
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class UserResponse(UserBase):
    """
    Schema for user data in API responses
    Excludes sensitive information like password
    """
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        """
        Pydantic configuration
        Allows conversion from ORM models
        """
        from_attributes = True


class UserUpdate(BaseModel):
    """
    Schema for updating user information
    All fields are optional
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class PasswordResetRequest(BaseModel):
    """
    Schema for requesting password reset
    User provides their email
    """
    email: EmailStr = Field(..., description="Registered email address")


class PasswordResetConfirm(BaseModel):
    """
    Schema for confirming password reset
    User provides token from email and new password
    """
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate new password strength
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class Token(BaseModel):
    """
    Schema for JWT token response
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")


class TokenData(BaseModel):
    """
    Schema for decoded token data
    """
    username: Optional[str] = None
    user_id: Optional[int] = None