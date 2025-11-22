"""
Configuration file for CCTV Security System
This file contains all configuration settings and environment variables
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application settings class
    Uses pydantic for environment variable validation
    """
    
    # Application settings
    APP_NAME: str = "CCTV Security Monitor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database settings
    # SQLite database file path
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/database/cctv_security.db"
    
    # Security settings
    # Secret key for JWT token generation (CHANGE THIS IN PRODUCTION!)
    SECRET_KEY: str = "your-secret-key-change-this-in-production-09876543210"
    # Algorithm for JWT encoding
    ALGORITHM: str = "HS256"
    # Token expiration time in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    # Password reset token expiration in minutes
    RESET_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email settings (for password reset)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None  # Your email
    SMTP_PASSWORD: Optional[str] = None  # Your email password or app password
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: str = "CCTV Security System"
    
    # File upload settings
    # Maximum file size for image uploads (10MB)
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    # Directory for storing uploaded images
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    # Directory for storing logs
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # AI Detection settings
    # YOLO model path
    YOLO_MODEL_PATH: str = "yolov8n.pt"  # Will download automatically if not exists
    # Confidence threshold for object detection (0-1)
    DETECTION_CONFIDENCE: float = 0.5
    # Time in seconds to wait between detections to avoid spam
    DETECTION_COOLDOWN: int = 5
    
    # Camera settings
    # Default camera source (0 for webcam, or RTSP URL for IP camera)
    CAMERA_SOURCE: str = "0"
    # FPS for video processing
    CAMERA_FPS: int = 30
    
    # Firebase settings (for push notifications)
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    class Config:
        """
        Pydantic configuration
        Allows reading from .env file
        """
        env_file = ".env"
        case_sensitive = True


# Create settings instance
# This will be imported throughout the application
settings = Settings()


# Create necessary directories if they don't exist
def create_directories():
    """
    Create required directories for the application
    Called during application startup
    """
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "database").mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directories: uploads, logs, database")


if __name__ == "__main__":
    # Test configuration loading
    create_directories()
    print(f"App Name: {settings.APP_NAME}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Upload Directory: {settings.UPLOAD_DIR}")
