"""
Models package initialization
Imports all database models for easy access
"""

# Import all models here so they are registered with SQLAlchemy Base
# This is important for database.init_db() to work correctly
from app.models.user import User
from app.models.event import Event
from app.models.password_reset import PasswordResetToken

# Export all models
# This allows: from app.models import User, Event, PasswordResetToken
__all__ = ["User", "Event", "PasswordResetToken"]
