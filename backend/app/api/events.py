"""
Events API endpoints
Handles event retrieval, marking as read, and statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_user_owns_resource
from app.models.user import User
from app.schemas.event import (
    EventResponse,
    EventCreate,
    EventUpdate,
    EventListResponse,
    EventStatistics
)
from app.services.event_service import EventService

# Create API router
router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new security event
    
    **Request Body:**
    - user_id: User ID who owns the camera
    - event_type: Type of event (theft, suspicious_behavior, etc.)
    - description: Event description
    - confidence: Detection confidence (0-1)
    - image_path: Path to saved image (optional)
    - camera_id: Camera identifier (optional)
    - latitude/longitude: GPS coordinates (optional)
    
    **Returns:**
    - Created event information
    
    **Note:**
    In production, this endpoint should be protected and only called by the surveillance system.
    """
    try:
        new_event = EventService.create_event(
            db=db,
            user_id=event_data.user_id,
            event_type=event_data.event_type,
            description=event_data.description,
            confidence=event_data.confidence,
            image_path=event_data.image_path,
            camera_id=event_data.camera_id,
            latitude=event_data.latitude,
            longitude=event_data.longitude
        )
        
        return new_event
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=EventListResponse)
async def get_user_events(
    user_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    unread_only: bool = Query(False, description="Show only unread events"),
    db: Session = Depends(get_db)
):
    """
    Get events for a specific user with pagination
    
    **Parameters:**
    - user_id: User ID
    - page: Page number (starts at 1)
    - page_size: Number of items per page (1-100)
    - unread_only: If true, only return unread events
    
    **Returns:**
    - Paginated list of events with total count
    
    **Note:**
    In production, add authentication to ensure users can only access their own events.
    """
    # Calculate skip value for pagination
    skip = (page - 1) * page_size
    
    # Get events
    events = EventService.get_user_events(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=page_size,
        unread_only=unread_only
    )
    
    # Get total count
    all_events = EventService.get_user_events(
        db=db,
        user_id=user_id,
        skip=0,
        limit=10000  # Get all for counting
    )
    total = len(all_events)
    
    # Get unread count
    unread = EventService.get_unread_count(db=db, user_id=user_id)
    
    return EventListResponse(
        total=total,
        unread=unread,
        events=events,
        page=page,
        page_size=page_size
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific event by ID
    
    **Parameters:**
    - event_id: Event ID
    
    **Returns:**
    - Event information
    
    **Errors:**
    - 404: Event not found
    """
    event = EventService.get_event_by_id(db, event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event


@router.patch("/{event_id}/read", response_model=EventResponse)
async def mark_event_as_read(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark an event as read
    
    **Parameters:**
    - event_id: Event ID
    
    **Returns:**
    - Updated event information
    
    **Errors:**
    - 404: Event not found
    """
    event = EventService.mark_event_as_read(db, event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event


@router.post("/user/{user_id}/mark-all-read")
async def mark_all_events_as_read(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark all events as read for a user
    
    **Parameters:**
    - user_id: User ID
    
    **Returns:**
    - Number of events marked as read
    """
    count = EventService.mark_all_as_read(db, user_id)
    
    return {
        "message": f"Marked {count} events as read",
        "count": count
    }


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an event
    
    **Parameters:**
    - event_id: Event ID
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 404: Event not found
    """
    success = EventService.delete_event(db, event_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return {"message": "Event deleted successfully"}


@router.get("/user/{user_id}/statistics", response_model=EventStatistics)
async def get_event_statistics(
    user_id: int,
    days: int = Query(7, ge=1, le=365, description="Number of days to include"),
    db: Session = Depends(get_db)
):
    """
    Get event statistics for a user
    
    **Parameters:**
    - user_id: User ID
    - days: Number of days to include in statistics (1-365)
    
    **Returns:**
    - Statistics including total events, breakdown by type, by day, etc.
    """
    stats = EventService.get_event_statistics(db, user_id, days)
    
    return EventStatistics(**stats)


@router.get("/user/{user_id}/unread-count")
async def get_unread_count(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get count of unread events for a user
    
    **Parameters:**
    - user_id: User ID
    
    **Returns:**
    - Count of unread events
    """
    count = EventService.get_unread_count(db, user_id)
    
    return {
        "user_id": user_id,
        "unread_count": count
    }


# Health check for events API
@router.get("/health/check")
async def events_health_check():
    """
    Health check endpoint for events API
    
    **Returns:**
    - Status information
    """
    return {
        "status": "ok",
        "service": "events",
        "message": "Events API is running"
    }