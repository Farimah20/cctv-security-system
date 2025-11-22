import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import os

os.environ['QT_QPA_PLATFORM'] = 'xcb'

from app.detection.surveillance_system import SurveillanceSystem

VIDEO_PATH = "../test_videos/people_test.mp4"

def on_event(event):
    print(f"\n🚨 ALERT: {event['behavior_type']}")
    print(f"   {event['description']}")
    print(f"   Confidence: {event['confidence']:.2%}")

print("Testing with video file:", VIDEO_PATH)
system = SurveillanceSystem(
    camera_source=VIDEO_PATH,
    on_suspicious_event=on_event
)
system.start_monitoring(show_preview=True)
