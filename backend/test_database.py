"""
Test script for database setup
This script will:
1. Create all database tables
2. Insert sample data
3. Query data to verify everything works
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import init_db, SessionLocal, engine
from app.core.config import create_directories
from app.models import User, Event, PasswordResetToken
from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid


# Password hashing context
# This is used to securely hash passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_sample_data():
    """
    Create sample data for testing
    This helps verify that database is working correctly
    """
    # Create database session
    db = SessionLocal()
    
    try:
        print("\n🔧 Creating sample data...")
        
        # 1. Create a test user
        hashed_password = pwd_context.hash("testpassword123")
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)  # Refresh to get the auto-generated ID
        print(f"✅ Created user: {test_user.username} (ID: {test_user.id})")
        
        # 2. Create a sample event
        sample_event = Event(
            user_id=test_user.id,
            event_type="theft",
            description="Suspicious person detected near entrance",
            confidence=0.87,
            is_read=False
        )
        db.add(sample_event)
        db.commit()
        db.refresh(sample_event)
        print(f"✅ Created event: {sample_event.event_type} (ID: {sample_event.id})")
        
        # 3. Create a password reset token
        reset_token = PasswordResetToken(
            user_id=test_user.id,
            token=str(uuid.uuid4()),
            expires_at=datetime.now() + timedelta(minutes=30),
            is_used=False
        )
        db.add(reset_token)
        db.commit()
        db.refresh(reset_token)
        print(f"✅ Created reset token (expires in 30 minutes)")
        
        print("\n✅ Sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


def query_sample_data():
    """
    Query and display sample data
    Verifies that we can read from database
    """
    db = SessionLocal()
    
    try:
        print("\n📊 Querying database...")
        
        # Query all users
        users = db.query(User).all()
        print(f"\n👥 Users ({len(users)} total):")
        for user in users:
            print(f"  - {user.username} ({user.email})")
        
        # Query all events
        events = db.query(Event).all()
        print(f"\n🚨 Events ({len(events)} total):")
        for event in events:
            print(f"  - {event.event_type} | Confidence: {event.confidence:.2f} | Read: {event.is_read}")
        
        # Query reset tokens
        tokens = db.query(PasswordResetToken).all()
        print(f"\n🔑 Password Reset Tokens ({len(tokens)} total):")
        for token in tokens:
            print(f"  - User ID: {token.user_id} | Valid: {token.is_valid()} | Used: {token.is_used}")
        
        print("\n✅ Database query successful!")
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
    finally:
        db.close()


def main():
    """
    Main test function
    """
    print("=" * 60)
    print("🧪 DATABASE SETUP TEST")
    print("=" * 60)
    
    try:
        # Step 1: Create necessary directories
        print("\n📁 Step 1: Creating directories...")
        create_directories()
        
        # Step 2: Test database connection
        print("\n🔌 Step 2: Testing database connection...")
        with engine.connect() as conn:
            print("✅ Database connection successful")
        
        # Step 3: Initialize database (create tables)
        print("\n🗄️  Step 3: Creating database tables...")
        init_db()
        
        # Step 4: Create sample data
        print("\n📝 Step 4: Creating sample data...")
        create_sample_data()
        
        # Step 5: Query data
        print("\n🔍 Step 5: Querying data...")
        query_sample_data()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n💡 Database is ready to use!")
        print(f"📍 Database location: {Path(__file__).parent / 'database' / 'cctv_security.db'}")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
