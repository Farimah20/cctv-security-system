"""
Password Reset Token model
Stores temporary tokens for password reset functionality
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.core.database import Base


class PasswordResetToken(Base):
    """
    Password reset token model
    
    When user requests password reset:
    1. Generate unique token
    2. Store it here with expiration time
    3. Send token to user's email
    4. User clicks link with token
    5. Verify token is valid and not expired
    6. Allow password change
    7. Mark token as used
    
    Attributes:
        id: Unique identifier
        user_id: Foreign key to user requesting reset
        token: Unique random token (UUID or similar)
        expires_at: When this token expires (typically 30 minutes)
        is_used: Whether token has been used (one-time use only)
        created_at: When token was created
    """
    
    # Table name
    __tablename__ = "password_reset_tokens"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Unique token string (will be UUID4)
    # Indexed for fast lookups when user clicks reset link
    token = Column(String(100), unique=True, nullable=False, index=True)
    
    # Expiration timestamp
    # Typically set to 30 minutes from creation
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Whether token has been used
    # Tokens can only be used once for security
    is_used = Column(Boolean, default=False, nullable=False)
    
    # Creation timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="password_reset_tokens")
    
    def is_valid(self) -> bool:
        """
        Check if token is still valid
        
        Token is valid if:
        - It hasn't been used yet
        - It hasn't expired
        
        Returns:
            bool: True if valid, False otherwise
        """
        now = datetime.now()
        return not self.is_used and self.expires_at > now
    
    def mark_as_used(self):
        """
        Mark token as used
        Should be called after successful password reset
        """
        self.is_used = True
    
    def __repr__(self):
        """
        String representation
        """
        return (
            f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, "
            f"is_used={self.is_used}, expires_at={self.expires_at})>"
        )
    
    def to_dict(self):
        """
        Convert to dictionary
        Note: Never expose the actual token in API responses for security
        
        Returns:
            dict: Token metadata (without actual token string)
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "is_used": self.is_used,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_valid": self.is_valid()
        }
