"""
Integrated Surveillance System
Combines object detection and behavior analysis
"""

import cv2
import numpy as np
from typing import Optional, Callable, Dict, List
from datetime import datetime
from pathlib import Path
import time

from app.detection.object_detector import ObjectDetector
from app.detection.behavior_analyzer import BehaviorAnalyzer
from app.core.config import settings


class SurveillanceSystem:
    """
    Complete surveillance system
    Processes video, detects objects, analyzes behavior, and triggers alerts
    """
    
    def __init__(
        self,
        camera_source: str = "0",
        on_suspicious_event: Optional[Callable] = None
    ):
        """
        Initialize surveillance system
        
        Args:
            camera_source: Camera source (0 for webcam, RTSP URL for IP camera)
            on_suspicious_event: Callback function for suspicious events
        """
        print("🔧 Initializing Surveillance System...")
        
        # Initialize components
        self.object_detector = ObjectDetector()
        self.behavior_analyzer = BehaviorAnalyzer()
        
        # Camera settings
        self.camera_source = camera_source if camera_source != "0" else 0
        self.camera = None
        
        # Callback for suspicious events
        self.on_suspicious_event = on_suspicious_event
        
        # Recording settings
        self.save_detections = True
        self.output_dir = settings.UPLOAD_DIR / "detections"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = time.time()
        
        # Status flags
        self.is_running = False
        self.last_alert_time = {}  # Track last alert time per event type
        
        print("✅ Surveillance System initialized!")
    
    
    def initialize_camera(self) -> bool:
        """
        Initialize camera connection
        
        Returns:
            True if successful, False otherwise
        """
        print(f"📹 Connecting to camera: {self.camera_source}")
        
        try:
            self.camera = cv2.VideoCapture(self.camera_source)
            
            if not self.camera.isOpened():
                print("❌ Failed to open camera")
                return False
            
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            print("✅ Camera connected successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            return False
    
    
    def process_frame(self, frame: np.ndarray) -> tuple[np.ndarray, List[Dict]]:
        """
        Process a single frame
        
        Args:
            frame: Input frame from camera
        
        Returns:
            Tuple of (annotated_frame, suspicious_events)
        """
        # Detect objects in frame
        detections = self.object_detector.detect_objects(frame)
        
        # Update behavior tracking
        self.behavior_analyzer.update_tracks(detections)
        
        # Detect suspicious behaviors
        suspicious_events = self.behavior_analyzer.detect_suspicious_behaviors()
        
        # Draw detections on frame
        annotated_frame = self.object_detector.draw_detections(
            frame, detections, show_labels=True
        )
        
        # Draw tracking info
        annotated_frame = self._draw_tracking_info(annotated_frame)
        
        # Highlight suspicious objects
        if suspicious_events:
            annotated_frame = self._highlight_suspicious_objects(
                annotated_frame, suspicious_events
            )
        
        return annotated_frame, suspicious_events
    
    
    def _draw_tracking_info(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw tracking information on frame
        
        Args:
            frame: Frame to annotate
        
        Returns:
            Annotated frame
        """
        # Get tracking info
        track_info = self.behavior_analyzer.get_tracking_info()
        
        # Draw background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 120), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        # Draw text
        y_offset = 35
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        y_offset += 25
        cv2.putText(frame, f"Tracked Objects: {track_info['total_tracked']}", 
                    (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        y_offset += 25
        cv2.putText(frame, f"Frame: {track_info['frame_count']}", 
                    (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return frame
    
    
    def _highlight_suspicious_objects(
        self,
        frame: np.ndarray,
        suspicious_events: List[Dict]
    ) -> np.ndarray:
        """
        Highlight suspicious objects with red overlay
        
        Args:
            frame: Frame to annotate
            suspicious_events: List of suspicious events
        
        Returns:
            Annotated frame
        """
        for event in suspicious_events:
            # Get position
            x, y = event['position']
            
            # Draw red circle around suspicious object
            cv2.circle(frame, (x, y), 50, (0, 0, 255), 3)
            
            # Draw alert text
            alert_text = f"ALERT: {event['behavior_type']}"
            cv2.putText(
                frame,
                alert_text,
                (x - 80, y - 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )
            
            # Draw confidence
            conf_text = f"Confidence: {event['confidence']:.2f}"
            cv2.putText(
                frame,
                conf_text,
                (x - 80, y - 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1
            )
        
        return frame
    
    
    def save_event_image(self, frame: np.ndarray, event: Dict) -> str:
        """
        Save image of suspicious event
        
        Args:
            frame: Frame to save
            event: Event information
        
        Returns:
            Path to saved image
        """
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        behavior_type = event['behavior_type']
        filename = f"{behavior_type}_{timestamp}.jpg"
        
        # Create subdirectory for this date
        date_dir = self.output_dir / datetime.now().strftime("%Y-%m-%d")
        date_dir.mkdir(exist_ok=True)
        
        # Full path
        filepath = date_dir / filename
        
        # Save image
        cv2.imwrite(str(filepath), frame)
        
        return str(filepath)
    
    
    def handle_suspicious_event(self, frame: np.ndarray, event: Dict):
        """
        Handle detected suspicious event
        
        Args:
            frame: Current frame
            event: Suspicious event information
        """
        # Check cooldown to avoid spam
        event_key = f"{event['object_id']}_{event['behavior_type']}"
        current_time = time.time()
        
        if event_key in self.last_alert_time:
            if current_time - self.last_alert_time[event_key] < settings.DETECTION_COOLDOWN:
                return  # Still in cooldown
        
        self.last_alert_time[event_key] = current_time
        
        # Save image
        if self.save_detections:
            image_path = self.save_event_image(frame, event)
            event['image_path'] = image_path
            print(f"📸 Saved event image: {image_path}")
        
        # Call callback if provided
        if self.on_suspicious_event:
            try:
                self.on_suspicious_event(event)
            except Exception as e:
                print(f"❌ Error in event callback: {e}")
        
        # Print alert
        print("\n" + "="*60)
        print(f"🚨 SUSPICIOUS ACTIVITY DETECTED!")
        print(f"   Type: {event['behavior_type']}")
        print(f"   Description: {event['description']}")
        print(f"   Confidence: {event['confidence']:.2%}")
        print(f"   Position: {event['position']}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
    
    
    def start_monitoring(self, show_preview: bool = True):
        """
        Start continuous monitoring
        
        Args:
            show_preview: Whether to show video preview window
        """
        if not self.initialize_camera():
            return
        
        self.is_running = True
        print("\n🎥 Starting surveillance monitoring...")
        print("   Press 'q' to quit")
        print("   Press 's' to save current frame")
        print("="*60 + "\n")
        
        try:
            while self.is_running:
                # Read frame
                ret, frame = self.camera.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                # Process frame
                annotated_frame, suspicious_events = self.process_frame(frame)
                
                # Handle suspicious events
                for event in suspicious_events:
                    self.handle_suspicious_event(frame, event)
                
                # Update FPS
                self.frame_count += 1
                if self.frame_count % 30 == 0:
                    elapsed = time.time() - self.fps_start_time
                    self.fps = 30 / elapsed
                    self.fps_start_time = time.time()
                
                # Show preview
                if show_preview:
                    cv2.imshow('Surveillance Monitor', annotated_frame)
                    
                    # Handle key press
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("\n👋 Stopping surveillance...")
                        break
                    elif key == ord('s'):
                        # Manual save
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filepath = self.output_dir / f"manual_{timestamp}.jpg"
                        cv2.imwrite(str(filepath), frame)
                        print(f"📸 Saved: {filepath}")
        
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
        
        finally:
            self.stop_monitoring()
    
    
    def stop_monitoring(self):
        """
        Stop monitoring and cleanup resources
        """
        self.is_running = False
        
        if self.camera is not None:
            self.camera.release()
        
        cv2.destroyAllWindows()
        
        print("\n✅ Surveillance system stopped")
        print(f"   Total frames processed: {self.frame_count}")
        print(f"   Average FPS: {self.fps:.2f}")


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("🎥 SURVEILLANCE SYSTEM TEST")
    print("=" * 60)
    
    # Define callback for suspicious events
    def on_event(event: Dict):
        print(f"\n🔔 Event callback triggered: {event['behavior_type']}")
    
    # Create surveillance system
    system = SurveillanceSystem(
        camera_source="0",  # Use webcam
        on_suspicious_event=on_event
    )
    
    # Start monitoring
    system.start_monitoring(show_preview=True)
