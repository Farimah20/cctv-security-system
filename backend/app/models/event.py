"""
Event model for database
Stores detection events (theft, suspicious behavior, etc.)
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Event(Base):
    """
    Event model for storing detected security events
    
    Attributes:
        id: Unique identifier for event
        user_id: Foreign key to user who owns this camera
        event_type: Type of event (theft, suspicious_behavior, loitering, etc.)
        description: Detailed description of what was detected
        image_path: Path to saved image/video frame
        confidence: AI model confidence score (0.0 to 1.0)
        timestamp: When the event occurred
        is_read: Whether user has seen this notification
        latitude: GPS latitude (optional, for multiple camera locations)
        longitude: GPS longitude (optional)
        camera_id: Identifier for specific camera (if user has multiple cameras)
    """
    
    # Table name in database
    __tablename__ = "events"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to users table
    # When user is deleted, their events are also deleted (CASCADE)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Event type - indexed for fast filtering
    # Examples: 'theft', 'suspicious_behavior', 'loitering', 'violence'
    event_type = Column(String(50), nullable=False, index=True)
    
    # Detailed description of the event
    description = Column(Text, nullable=True)
    
    # Path to saved image file
    # Example: 'uploads/events/2024/01/15/event_12345.jpg'
    image_path = Column(String(500), nullable=True)
    
    # AI model confidence score (0.0 to 1.0)
    # Higher values mean the model is more confident in its detection
    confidence = Column(Float, nullable=False, default=0.0)
    
    # When the event was detected
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Notification read status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Optional: GPS coordinates for multi-location setups
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Optional: Camera identifier for users with multiple cameras
    camera_id = Column(String(50), nullable=True, index=True)
    
    # Relationship back to user
    # This allows us to access event.user to get user details
    user = relationship("User", back_populates="events")
    
    def __repr__(self):
        """
        String representation of Event object
        """
        return (
            f"<Event(id={self.id}, type='{self.event_type}', "
            f"confidence={self.confidence:.2f}, user_id={self.user_id})>"
        )
    
    def to_dict(self):
        """
        Convert Event object to dictionary for API responses
        
        Returns:
            dict: Event data
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "description": self.description,
            "image_path": self.image_path,
            "confidence": round(self.confidence, 2),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_read": self.is_read,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "camera_id": self.camera_id
        }
