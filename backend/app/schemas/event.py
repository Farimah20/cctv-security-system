"""
Pydantic schemas for event-related data validation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    """
    Base schema for event
    """
    event_type: str = Field(..., description="Type of event")
    description: Optional[str] = Field(None, description="Event description")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence (0-1)")
    camera_id: Optional[str] = Field(None, description="Camera identifier")
    latitude: Optional[float] = Field(None, description="GPS latitude")
    longitude: Optional[float] = Field(None, description="GPS longitude")


class EventCreate(EventBase):
    """
    Schema for creating an event
    """
    user_id: int = Field(..., description="User ID")
    image_path: Optional[str] = Field(None, description="Path to saved image")


class EventResponse(EventBase):
    """
    Schema for event response
    """
    id: int
    user_id: int
    image_path: Optional[str] = None
    is_read: bool
    timestamp: datetime
    
    class Config:
        """
        Pydantic configuration
        """
        from_attributes = True


class EventUpdate(BaseModel):
    """
    Schema for updating an event
    """
    is_read: Optional[bool] = None
    description: Optional[str] = None


class EventListResponse(BaseModel):
    """
    Schema for paginated event list response
    """
    total: int = Field(..., description="Total number of events")
    unread: int = Field(..., description="Number of unread events")
    events: list[EventResponse] = Field(..., description="List of events")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")


class EventStatistics(BaseModel):
    """
    Schema for event statistics
    """
    total_events: int
    by_type: dict[str, int]
    by_day: dict[str, int]
    average_confidence: float
    date_range: dict[str, str]
