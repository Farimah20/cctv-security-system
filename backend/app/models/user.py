"""
User model for database
Defines the structure of users table
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """
    User model for storing user account information
    
    Attributes:
        id: Unique identifier for user
        username: Unique username for login
        email: User's email address (unique)
        hashed_password: Bcrypt hashed password (never store plain passwords!)
        is_active: Whether the account is active or disabled
        is_superuser: Whether user has admin privileges
        created_at: Timestamp when account was created
        updated_at: Timestamp when account was last updated
    """
    
    # Table name in database
    __tablename__ = "users"
    
    # Primary key - auto-incrementing integer
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Username - must be unique and indexed for fast lookups
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # Email - must be unique and indexed
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    # Hashed password - never store plain passwords!
    # Will store bcrypt hash (60 characters)
    hashed_password = Column(String(255), nullable=False)
    
    # Account status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Timestamps - automatically set by database
    # func.now() uses database's current timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships to other tables
    # This creates a relationship to Event model (one user can have many events)
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    
    # Relationship to password reset tokens
    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        """
        String representation of User object
        Useful for debugging
        """
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self):
        """
        Convert User object to dictionary
        Used for API responses (excludes sensitive data like password)
        
        Returns:
            dict: User data without sensitive information
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
