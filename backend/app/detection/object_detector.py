"""
Object Detection using YOLOv8
Detects people, bags, and other objects in video frames
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import time

from app.core.config import settings


class ObjectDetector:
    """
    Object detector using YOLOv8
    Detects objects in images and video frames
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize YOLO model
        
        Args:
            model_path: Path to YOLO model file (default: yolov8n.pt)
        """
        # Use default model if not specified
        if model_path is None:
            model_path = settings.YOLO_MODEL_PATH
        
        print(f"📦 Loading YOLO model: {model_path}")
        
        # Load YOLO model
        # On first run, this will download the model automatically
        self.model = YOLO(model_path)
        
        # Confidence threshold for detections
        self.confidence_threshold = settings.DETECTION_CONFIDENCE
        
        # COCO dataset class names (what YOLO can detect)
        self.class_names = self.model.names
        
        print(f"✅ YOLO model loaded successfully!")
        print(f"   Model can detect {len(self.class_names)} object types")
        print(f"   Confidence threshold: {self.confidence_threshold}")
    
    
    def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in a single frame
        
        Args:
            frame: Image frame (BGR format from OpenCV)
        
        Returns:
            List of detected objects with their properties
            Each detection contains:
            - class_id: Object class ID
            - class_name: Object class name (e.g., 'person', 'backpack')
            - confidence: Detection confidence (0-1)
            - bbox: Bounding box [x1, y1, x2, y2]
            - center: Center point (x, y)
        """
        # Run YOLO inference on the frame
        results = self.model(frame, verbose=False)
        
        detections = []
        
        # Process each detection
        for result in results:
            # Get detection boxes
            boxes = result.boxes
            
            for box in boxes:
                # Get detection data
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.class_names[class_id]
                
                # Only keep detections above confidence threshold
                if confidence < self.confidence_threshold:
                    continue
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Calculate center point
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                
                # Calculate width and height
                width = int(x2 - x1)
                height = int(y2 - y1)
                
                # Create detection dictionary
                detection = {
                    'class_id': class_id,
                    'class_name': class_name,
                    'confidence': confidence,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': (center_x, center_y),
                    'width': width,
                    'height': height
                }
                
                detections.append(detection)
        
        return detections
    
    
    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Dict],
        show_labels: bool = True
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Image frame
            detections: List of detections from detect_objects()
            show_labels: Whether to show labels and confidence
        
        Returns:
            Frame with drawn detections
        """
        # Create a copy to avoid modifying original
        annotated_frame = frame.copy()
        
        # Draw each detection
        for det in detections:
            # Get coordinates
            x1, y1, x2, y2 = det['bbox']
            
            # Choose color based on class
            if det['class_name'] == 'person':
                color = (0, 255, 0)  # Green for people
            elif det['class_name'] in ['backpack', 'handbag', 'suitcase']:
                color = (255, 165, 0)  # Orange for bags
            else:
                color = (0, 165, 255)  # Orange-red for other objects
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label if requested
            if show_labels:
                label = f"{det['class_name']} {det['confidence']:.2f}"
                
                # Get text size for background
                (text_width, text_height), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                
                # Draw background rectangle for text
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1 - text_height - 10),
                    (x1 + text_width, y1),
                    color,
                    -1
                )
                
                # Draw text
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )
            
            # Draw center point
            cv2.circle(
                annotated_frame,
                det['center'],
                3,
                color,
                -1
            )
        
        return annotated_frame
    
    
    def filter_detections_by_class(
        self,
        detections: List[Dict],
        class_names: List[str]
    ) -> List[Dict]:
        """
        Filter detections to only include specific classes
        
        Args:
            detections: List of all detections
            class_names: List of class names to keep
        
        Returns:
            Filtered list of detections
        """
        return [
            det for det in detections
            if det['class_name'] in class_names
        ]
    
    
    def count_objects(self, detections: List[Dict]) -> Dict[str, int]:
        """
        Count objects by class
        
        Args:
            detections: List of detections
        
        Returns:
            Dictionary mapping class names to counts
        """
        counts = {}
        for det in detections:
            class_name = det['class_name']
            counts[class_name] = counts.get(class_name, 0) + 1
        return counts


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 OBJECT DETECTOR TEST")
    print("=" * 60)
    
    # Initialize detector
    detector = ObjectDetector()
    
    # Test with webcam (if available)
    print("\n📹 Testing with webcam (press 'q' to quit)...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        exit()
    
    fps_start_time = time.time()
    frame_count = 0
    
    while True:
        # Read frame
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect objects
        detections = detector.detect_objects(frame)
        
        # Draw detections
        annotated_frame = detector.draw_detections(frame, detections)
        
        # Count objects
        counts = detector.count_objects(detections)
        
        # Calculate FPS
        frame_count += 1
        if frame_count % 30 == 0:
            fps = 30 / (time.time() - fps_start_time)
            fps_start_time = time.time()
            print(f"FPS: {fps:.2f} | Detections: {counts}")
        
        # Add FPS to frame
        cv2.putText(
            annotated_frame,
            f"Objects: {len(detections)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        
        # Show frame
        cv2.imshow('Object Detection Test', annotated_frame)
        
        # Break on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n✅ Object detector test completed!")
