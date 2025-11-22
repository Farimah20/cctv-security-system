"""
Behavior Analyzer
Analyzes object movements and detects suspicious behaviors
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import math


class TrackedObject:
    """
    Represents a tracked object across multiple frames
    Stores position history and calculates movement patterns
    """
    
    def __init__(self, object_id: int, detection: Dict, frame_number: int):
        """
        Initialize tracked object
        
        Args:
            object_id: Unique ID for this object
            detection: Detection dictionary from ObjectDetector
            frame_number: Current frame number
        """
        self.id = object_id
        self.class_name = detection['class_name']
        self.first_seen = frame_number
        self.last_seen = frame_number
        
        # Position history (stores last N positions)
        self.position_history = deque(maxlen=30)  # Keep last 30 positions
        self.position_history.append(detection['center'])
        
        # Bounding box history
        self.bbox_history = deque(maxlen=30)
        self.bbox_history.append(detection['bbox'])
        
        # Movement statistics
        self.total_distance = 0.0
        self.is_stationary = False
        self.stationary_frames = 0
        
        # Behavior flags
        self.suspicious_behavior = False
        self.behavior_type = None
        self.confidence = 0.0
    
    
    def update(self, detection: Dict, frame_number: int):
        """
        Update tracked object with new detection
        
        Args:
            detection: New detection dictionary
            frame_number: Current frame number
        """
        self.last_seen = frame_number
        
        # Get previous and current positions
        prev_pos = self.position_history[-1]
        curr_pos = detection['center']
        
        # Calculate distance moved
        distance = math.sqrt(
            (curr_pos[0] - prev_pos[0])**2 +
            (curr_pos[1] - prev_pos[1])**2
        )
        
        self.total_distance += distance
        
        # Update position history
        self.position_history.append(curr_pos)
        self.bbox_history.append(detection['bbox'])
        
        # Check if stationary (moved less than 10 pixels)
        if distance < 10:
            self.stationary_frames += 1
            if self.stationary_frames > 30:  # Stationary for 30 frames
                self.is_stationary = True
        else:
            self.stationary_frames = 0
            self.is_stationary = False
    
    
    def get_speed(self) -> float:
        """
        Calculate average speed over last 10 frames
        
        Returns:
            Average speed in pixels per frame
        """
        if len(self.position_history) < 2:
            return 0.0
        
        # Take last 10 positions (or all if less)
        recent_positions = list(self.position_history)[-10:]
        
        total_distance = 0.0
        for i in range(1, len(recent_positions)):
            prev = recent_positions[i-1]
            curr = recent_positions[i]
            distance = math.sqrt(
                (curr[0] - prev[0])**2 +
                (curr[1] - prev[1])**2
            )
            total_distance += distance
        
        return total_distance / (len(recent_positions) - 1)
    
    
    def get_direction(self) -> Tuple[float, float]:
        """
        Calculate movement direction vector
        
        Returns:
            (dx, dy) normalized direction vector
        """
        if len(self.position_history) < 2:
            return (0.0, 0.0)
        
        start = self.position_history[0]
        end = self.position_history[-1]
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        # Normalize
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            return (dx / magnitude, dy / magnitude)
        
        return (0.0, 0.0)
    
    
    def is_moving_fast(self, threshold: float = 15.0) -> bool:
        """
        Check if object is moving fast
        
        Args:
            threshold: Speed threshold in pixels per frame
        
        Returns:
            True if moving fast
        """
        return self.get_speed() > threshold
    
    
    def time_in_view(self) -> int:
        """
        Get number of frames object has been in view
        
        Returns:
            Number of frames
        """
        return self.last_seen - self.first_seen + 1


class BehaviorAnalyzer:
    """
    Analyzes behavior patterns to detect suspicious activities
    """
    
    def __init__(self):
        """
        Initialize behavior analyzer
        """
        # Dictionary to store tracked objects {object_id: TrackedObject}
        self.tracked_objects: Dict[int, TrackedObject] = {}
        
        # Counter for assigning unique IDs
        self.next_object_id = 0
        
        # Frame counter
        self.frame_count = 0
        
        # Thresholds for suspicious behavior
        self.FAST_MOVEMENT_THRESHOLD = 15.0  # pixels per frame
        self.LOITERING_THRESHOLD = 150  # frames (5 seconds at 30 fps)
        self.ERRATIC_MOVEMENT_THRESHOLD = 5.0  # direction changes per second
        
        # Cooldown to avoid duplicate alerts
        self.alert_cooldown = {}  # {object_id: last_alert_frame}
        self.ALERT_COOLDOWN_FRAMES = 90  # 3 seconds at 30 fps
    
    
    def match_detection_to_tracked(
        self,
        detection: Dict,
        max_distance: float = 100.0
    ) -> Optional[int]:
        """
        Match a new detection to existing tracked object
        Uses nearest neighbor matching based on position
        
        Args:
            detection: Detection dictionary
            max_distance: Maximum distance for matching
        
        Returns:
            ID of matched tracked object, or None if no match
        """
        best_match_id = None
        best_distance = max_distance
        
        curr_pos = detection['center']
        
        # Find closest tracked object of same class
        for obj_id, tracked_obj in self.tracked_objects.items():
            # Only match same class
            if tracked_obj.class_name != detection['class_name']:
                continue
            
            # Check if object was seen recently (within last 10 frames)
            if self.frame_count - tracked_obj.last_seen > 10:
                continue
            
            # Calculate distance
            last_pos = tracked_obj.position_history[-1]
            distance = math.sqrt(
                (curr_pos[0] - last_pos[0])**2 +
                (curr_pos[1] - last_pos[1])**2
            )
            
            if distance < best_distance:
                best_distance = distance
                best_match_id = obj_id
        
        return best_match_id
    
    
    def update_tracks(self, detections: List[Dict]):
        """
        Update tracked objects with new detections
        
        Args:
            detections: List of detections from current frame
        """
        self.frame_count += 1
        
        # Match detections to existing tracks
        matched_ids = set()
        
        for detection in detections:
            # Try to match to existing track
            matched_id = self.match_detection_to_tracked(detection)
            
            if matched_id is not None:
                # Update existing track
                self.tracked_objects[matched_id].update(detection, self.frame_count)
                matched_ids.add(matched_id)
            else:
                # Create new track
                new_id = self.next_object_id
                self.next_object_id += 1
                
                self.tracked_objects[new_id] = TrackedObject(
                    new_id, detection, self.frame_count
                )
                matched_ids.add(new_id)
        
        # Remove old tracks (not seen for 30 frames)
        to_remove = []
        for obj_id, tracked_obj in self.tracked_objects.items():
            if self.frame_count - tracked_obj.last_seen > 30:
                to_remove.append(obj_id)
        
        for obj_id in to_remove:
            del self.tracked_objects[obj_id]
    
    
    def detect_suspicious_behaviors(self) -> List[Dict]:
        """
        Detect suspicious behaviors in tracked objects
        
        Returns:
            List of suspicious behavior events
            Each event contains:
            - object_id: ID of suspicious object
            - behavior_type: Type of suspicious behavior
            - confidence: Confidence score (0-1)
            - description: Human-readable description
            - position: Current position
        """
        suspicious_events = []
        
        for obj_id, tracked_obj in self.tracked_objects.items():
            # Only analyze people for now
            if tracked_obj.class_name != 'person':
                continue
            
            # Check alert cooldown
            if obj_id in self.alert_cooldown:
                if self.frame_count - self.alert_cooldown[obj_id] < self.ALERT_COOLDOWN_FRAMES:
                    continue
            
            # Behavior 1: Fast movement (possible theft/escape)
            if tracked_obj.is_moving_fast(self.FAST_MOVEMENT_THRESHOLD):
                if tracked_obj.time_in_view() > 10:  # Must be tracked for at least 10 frames
                    suspicious_events.append({
                        'object_id': obj_id,
                        'behavior_type': 'fast_movement',
                        'confidence': min(tracked_obj.get_speed() / 30.0, 1.0),
                        'description': 'Person moving unusually fast (possible theft/escape)',
                        'position': tracked_obj.position_history[-1],
                        'class_name': tracked_obj.class_name
                    })
                    self.alert_cooldown[obj_id] = self.frame_count
            
            # Behavior 2: Loitering (staying in one place too long)
            if tracked_obj.is_stationary and tracked_obj.time_in_view() > self.LOITERING_THRESHOLD:
                suspicious_events.append({
                    'object_id': obj_id,
                    'behavior_type': 'loitering',
                    'confidence': min(tracked_obj.time_in_view() / 300.0, 1.0),
                    'description': f'Person loitering for {tracked_obj.time_in_view()} frames',
                    'position': tracked_obj.position_history[-1],
                    'class_name': tracked_obj.class_name
                })
                self.alert_cooldown[obj_id] = self.frame_count
            
            # Behavior 3: Erratic movement (moving back and forth)
            if self.detect_erratic_movement(tracked_obj):
                suspicious_events.append({
                    'object_id': obj_id,
                    'behavior_type': 'erratic_movement',
                    'confidence': 0.7,
                    'description': 'Person showing erratic movement pattern',
                    'position': tracked_obj.position_history[-1],
                    'class_name': tracked_obj.class_name
                })
                self.alert_cooldown[obj_id] = self.frame_count
        
        return suspicious_events
    
    
    def detect_erratic_movement(self, tracked_obj: TrackedObject) -> bool:
        """
        Detect erratic/zigzag movement pattern
        
        Args:
            tracked_obj: Tracked object to analyze
        
        Returns:
            True if movement is erratic
        """
        if len(tracked_obj.position_history) < 10:
            return False
        
        # Calculate direction changes
        positions = list(tracked_obj.position_history)[-15:]
        direction_changes = 0
        
        for i in range(2, len(positions)):
            # Calculate vectors
            v1 = (positions[i-1][0] - positions[i-2][0],
                  positions[i-1][1] - positions[i-2][1])
            v2 = (positions[i][0] - positions[i-1][0],
                  positions[i][1] - positions[i-1][1])
            
            # Calculate angle between vectors
            if (v1[0]**2 + v1[1]**2) > 0 and (v2[0]**2 + v2[1]**2) > 0:
                dot_product = v1[0]*v2[0] + v1[1]*v2[1]
                mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
                mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
                
                cos_angle = dot_product / (mag1 * mag2)
                cos_angle = max(-1, min(1, cos_angle))  # Clamp to [-1, 1]
                
                angle = math.acos(cos_angle)
                
                # If angle > 90 degrees, it's a significant direction change
                if angle > math.pi / 2:
                    direction_changes += 1
        
        # If more than 5 direction changes in 15 frames, it's erratic
        return direction_changes >= 5
    
    
    def get_tracking_info(self) -> Dict:
        """
        Get current tracking statistics
        
        Returns:
            Dictionary with tracking information
        """
        return {
            'total_tracked': len(self.tracked_objects),
            'frame_count': self.frame_count,
            'tracked_by_class': self._count_by_class()
        }
    
    
    def _count_by_class(self) -> Dict[str, int]:
        """
        Count tracked objects by class
        
        Returns:
            Dictionary mapping class names to counts
        """
        counts = defaultdict(int)
        for tracked_obj in self.tracked_objects.values():
            counts[tracked_obj.class_name] += 1
        return dict(counts)
