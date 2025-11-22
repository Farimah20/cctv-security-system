"""
Test detection system
Tests object detection, behavior analysis, and surveillance system
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np
from app.detection.surveillance_system import SurveillanceSystem


def test_with_webcam():
    """
    Test surveillance system with webcam
    """
    print("\n" + "=" * 60)
    print("🎥 SURVEILLANCE SYSTEM TEST")
    print("=" * 60)
    print("\nThis test will:")
    print("1. Connect to your webcam")
    print("2. Detect objects (people, bags, etc.)")
    print("3. Track object movements")
    print("4. Detect suspicious behaviors:")
    print("   - Fast movement (possible theft/escape)")
    print("   - Loitering (staying too long)")
    print("   - Erratic movement (suspicious patterns)")
    print("\nControls:")
    print("   'q' - Quit")
    print("   's' - Save current frame")
    print("\n" + "=" * 60)
    
    input("\nPress Enter to start...")
    
    # Create surveillance system with event callback
    def handle_event(event):
        print(f"\n🚨 ALERT: {event['description']}")
        print(f"   Confidence: {event['confidence']:.2%}")
    
    system = SurveillanceSystem(
        #camera_source="0",
        camera_source="../test_videos/people_test.mp4",
        on_suspicious_event=handle_event
    )
    
    # Start monitoring
    system.start_monitoring(show_preview=True)


def test_with_sample_image():
    """
    Test object detection with a sample image
    """
    print("\n" + "=" * 60)
    print("🖼️  TESTING WITH SAMPLE IMAGE")
    print("=" * 60)
    
    from app.detection.object_detector import ObjectDetector
    
    # Create detector
    detector = ObjectDetector()
    
    # Create a simple test image with shapes
    # (In real usage, you'd load an actual image)
    test_image = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # Draw some shapes to represent objects
    cv2.rectangle(test_image, (100, 100), (200, 300), (0, 255, 0), -1)
    cv2.circle(test_image, (400, 200), 50, (255, 0, 0), -1)
    
    # Detect objects
    print("\n🔍 Detecting objects...")
    detections = detector.detect_objects(test_image)
    
    if detections:
        print(f"✅ Found {len(detections)} objects:")
        for det in detections:
            print(f"   - {det['class_name']}: {det['confidence']:.2%}")
    else:
        print("ℹ️  No objects detected (this is expected with blank image)")
    
    # Draw and show
    annotated = detector.draw_detections(test_image, detections)
    cv2.imshow('Test Image', annotated)
    print("\nPress any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    """
    Main test menu
    """
    print("\n" + "=" * 60)
    print("🧪 DETECTION SYSTEM TEST MENU")
    print("=" * 60)
    print("\nChoose a test:")
    print("1. Test with webcam (full surveillance system)")
    print("2. Test with sample image (object detection only)")
    print("3. Run both tests")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-3): ").strip()
    
    if choice == "1":
        test_with_webcam()
    elif choice == "2":
        test_with_sample_image()
    elif choice == "3":
        test_with_sample_image()
        input("\nPress Enter to continue to webcam test...")
        test_with_webcam()
    elif choice == "0":
        print("👋 Exiting...")
    else:
        print("❌ Invalid choice!")
        return main()


if __name__ == "__main__":
    main()
