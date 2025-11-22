"""
Event Service
Handles event creation, retrieval, and management
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from app.models.event import Event
from app.models.user import User


class EventService:
    """
    Service for managing security events
    """
    
    @staticmethod
    def create_event(
        db: Session,
        user_id: int,
        event_type: str,
        description: str,
        confidence: float,
        image_path: Optional[str] = None,
        camera_id: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Event:
        """
        Create a new security event
        
        Args:
            db: Database session
            user_id: ID of user who owns the camera
            event_type: Type of event (theft, suspicious_behavior, etc.)
            description: Event description
            confidence: Detection confidence (0-1)
            image_path: Path to saved image
            camera_id: Camera identifier
            latitude: GPS latitude
            longitude: GPS longitude
        
        Returns:
            Created Event object
        """
        # Create new event
        new_event = Event(
            user_id=user_id,
            event_type=event_type,
            description=description,
            confidence=confidence,
            image_path=image_path,
            camera_id=camera_id,
            latitude=latitude,
            longitude=longitude,
            is_read=False,
            timestamp=datetime.now()
        )
        
        # Add to database
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        
        return new_event
    
    
    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
        """
        Get event by ID
        
        Args:
            db: Database session
            event_id: Event ID
        
        Returns:
            Event object if found, None otherwise
        """
        return db.query(Event).filter(Event.id == event_id).first()
    
    
    @staticmethod
    def get_user_events(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        unread_only: bool = False
    ) -> List[Event]:
        """
        Get events for a specific user
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            unread_only: If True, only return unread events
        
        Returns:
            List of Event objects
        """
        query = db.query(Event).filter(Event.user_id == user_id)
        
        # Filter unread if requested
        if unread_only:
            query = query.filter(Event.is_read == False)
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(Event.timestamp))
        
        # Apply pagination
        events = query.offset(skip).limit(limit).all()
        
        return events
    
    
    @staticmethod
    def get_events_by_type(
        db: Session,
        user_id: int,
        event_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """
        Get events by type for a user
        
        Args:
            db: Database session
            user_id: User ID
            event_type: Type of event to filter
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of Event objects
        """
        events = db.query(Event).filter(
            Event.user_id == user_id,
            Event.event_type == event_type
        ).order_by(desc(Event.timestamp)).offset(skip).limit(limit).all()
        
        return events
    
    
    @staticmethod
    def get_events_by_date_range(
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Event]:
        """
        Get events within a date range
        
        Args:
            db: Database session
            user_id: User ID
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            List of Event objects
        """
        events = db.query(Event).filter(
            Event.user_id == user_id,
            Event.timestamp >= start_date,
            Event.timestamp <= end_date
        ).order_by(desc(Event.timestamp)).all()
        
        return events
    
    
    @staticmethod
    def mark_event_as_read(db: Session, event_id: int) -> Optional[Event]:
        """
        Mark an event as read
        
        Args:
            db: Database session
            event_id: Event ID
        
        Returns:
            Updated Event object if found, None otherwise
        """
        event = EventService.get_event_by_id(db, event_id)
        
        if event:
            event.is_read = True
            db.commit()
            db.refresh(event)
        
        return event
    
    
    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """
        Mark all events as read for a user
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            Number of events marked as read
        """
        count = db.query(Event).filter(
            Event.user_id == user_id,
            Event.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        
        return count
    
    
    @staticmethod
    def delete_event(db: Session, event_id: int) -> bool:
        """
        Delete an event
        
        Args:
            db: Database session
            event_id: Event ID
        
        Returns:
            True if deleted, False if not found
        """
        event = EventService.get_event_by_id(db, event_id)
        
        if event:
            db.delete(event)
            db.commit()
            return True
        
        return False
    
    
    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """
        Get count of unread events for a user
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            Number of unread events
        """
        count = db.query(Event).filter(
            Event.user_id == user_id,
            Event.is_read == False
        ).count()
        
        return count
    
    
    @staticmethod
    def get_event_statistics(db: Session, user_id: int, days: int = 7) -> Dict:
        """
        Get event statistics for the last N days
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to include in statistics
        
        Returns:
            Dictionary with statistics
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get events in range
        events = EventService.get_events_by_date_range(
            db, user_id, start_date, end_date
        )
        
        # Calculate statistics
        total_events = len(events)
        
        # Count by type
        by_type = {}
        for event in events:
            event_type = event.event_type
            by_type[event_type] = by_type.get(event_type, 0) + 1
        
        # Count by day
        by_day = {}
        for event in events:
            day = event.timestamp.strftime('%Y-%m-%d')
            by_day[day] = by_day.get(day, 0) + 1
        
        # Calculate average confidence
        avg_confidence = sum(e.confidence for e in events) / total_events if total_events > 0 else 0
        
        return {
            'total_events': total_events,
            'by_type': by_type,
            'by_day': by_day,
            'average_confidence': round(avg_confidence, 2),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
