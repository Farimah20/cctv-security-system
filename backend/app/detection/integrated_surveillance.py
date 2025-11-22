"""
Integrated Surveillance System with Database and Notifications
Combines detection, event storage, and notifications
"""

import cv2
import numpy as np
from typing import Optional, Callable, Dict
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.detection.surveillance_system import SurveillanceSystem
from app.core.database import SessionLocal
from app.services.event_service import EventService
from app.services.notification_service import NotificationService
from app.services.auth_service import AuthService


class IntegratedSurveillanceSystem(SurveillanceSystem):
    """
    Surveillance system with database and notification integration
    Extends SurveillanceSystem to add event storage and notifications
    """
    
    def __init__(
        self,
        user_id: int,
        camera_source: str = "0",
        camera_id: Optional[str] = None
    ):
        """
        Initialize integrated surveillance system
        
        Args:
            user_id: ID of user who owns this camera
            camera_source: Camera source (0 for webcam, RTSP URL for IP camera)
            camera_id: Optional camera identifier
        """
        # Initialize parent class
        super().__init__(camera_source=camera_source)
        
        # User and camera info
        self.user_id = user_id
        self.camera_id = camera_id or f"camera_{user_id}"
        
        # Get user information
        db = SessionLocal()
        try:
            self.user = AuthService.get_user_by_id(db, user_id)
            if not self.user:
                raise ValueError(f"User with ID {user_id} not found")
            
            print(f"✅ Surveillance system initialized for user: {self.user.username}")
        finally:
            db.close()
    
    
    def handle_suspicious_event(self, frame: np.ndarray, event: Dict):
        """
        Override parent method to add database storage and notifications
        
        Args:
            frame: Current frame
            event: Suspicious event information
        """
        # Call parent method for image saving and logging
        super().handle_suspicious_event(frame, event)
        
        # Get database session
        db = SessionLocal()
        
        try:
            # Store event in database
            db_event = EventService.create_event(
                db=db,
                user_id=self.user_id,
                event_type=event['behavior_type'],
                description=event['description'],
                confidence=event['confidence'],
                image_path=event.get('image_path'),
                camera_id=self.camera_id
            )
            
            print(f"💾 Event saved to database (ID: {db_event.id})")
            
            # Prepare event data for notification
            event_data = {
                'id': db_event.id,
                'event_type': db_event.event_type,
                'description': db_event.description,
                'confidence': db_event.confidence,
                'timestamp': db_event.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Send notifications
            notification_results = NotificationService.notify_user_of_event(
                user_email=self.user.email,
                user_name=self.user.username,
                user_fcm_token=None,  # TODO: Get from user preferences
                event=event_data
            )
            
            # Log notification results
            if notification_results['push']:
                print("📱 Push notification sent")
            if notification_results['email']:
                print("📧 Email notification sent")
            
        except Exception as e:
            print(f"❌ Error handling event: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            db.close()


# Test function
if __name__ == "__main__":
    """
    Test integrated surveillance system
    """
    print("=" * 60)
    print("🧪 INTEGRATED SURVEILLANCE SYSTEM TEST")
    print("=" * 60)
    
    # Get user ID
    print("\nNote: You need a user account in the database.")
    print("Default test user ID: 1")
    user_id_input = input("Enter user ID (or press Enter for 1): ").strip()
    user_id = int(user_id_input) if user_id_input else 1
    
    # Camera source
    print("\nCamera options:")
    print("  0 - Webcam")
    print("  <path> - Video file path")
    camera_input = input("Enter camera source (or press Enter for webcam): ").strip()
    camera_source = camera_input if camera_input else "0"
    
    try:
        # Create integrated surveillance system
        system = IntegratedSurveillanceSystem(
            user_id=user_id,
            camera_source=camera_source,
            camera_id=f"test_camera_{user_id}"
        )
        
        # Start monitoring
        print("\n" + "=" * 60)
        print("Starting surveillance with full integration:")
        print("  ✓ Object detection")
        print("  ✓ Behavior analysis")
        print("  ✓ Event storage in database")
        print("  ✓ Notifications")
        print("=" * 60)
        print("\nPress 'q' to quit\n")
        
        system.start_monitoring(show_preview=True)
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease create a user account first:")
        print("  python -m app.main")
        print("  Then use /auth/register endpoint")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()