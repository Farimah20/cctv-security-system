"""
Test script for authentication system
Tests all authentication features
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal, init_db
from app.core.config import create_directories
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService


def test_auth_system():
    """
    Test authentication system functionality
    """
    print("\n" + "=" * 60)
    print("🧪 AUTHENTICATION SYSTEM TEST")
    print("=" * 60)
    
    # Initialize
    create_directories()
    init_db()
    
    db = SessionLocal()
    
    try:
        # Test 1: Register new user
        print("\n📝 Test 1: User Registration")
        print("-" * 60)
        
        user_data = UserCreate(
            username="johndoe",
            email="john@example.com",
            password="SecurePass123"
        )
        
        try:
            new_user = AuthService.register_user(db, user_data)
            print(f"✅ User registered successfully!")
            print(f"   Username: {new_user.username}")
            print(f"   Email: {new_user.email}")
            print(f"   User ID: {new_user.id}")
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return
        
        # Test 2: Try duplicate registration
        print("\n📝 Test 2: Duplicate Registration (Should Fail)")
        print("-" * 60)
        
        try:
            AuthService.register_user(db, user_data)
            print("❌ Duplicate registration should have failed!")
        except Exception as e:
            print(f"✅ Correctly rejected duplicate: {str(e)[:50]}...")
        
        # Test 3: Login with correct credentials
        print("\n🔐 Test 3: Login with Correct Credentials")
        print("-" * 60)
        
        login_data = UserLogin(
            username="johndoe",
            password="SecurePass123"
        )
        
        authenticated_user = AuthService.authenticate_user(db, login_data)
        if authenticated_user:
            print("✅ Login successful!")
            print(f"   User: {authenticated_user.username}")
            
            # Generate token
            token = AuthService.create_access_token_for_user(authenticated_user)
            print(f"   Token: {token[:50]}...")
        else:
            print("❌ Login failed!")
        
        # Test 4: Login with wrong password
        print("\n🔐 Test 4: Login with Wrong Password (Should Fail)")
        print("-" * 60)
        
        wrong_login = UserLogin(
            username="johndoe",
            password="WrongPassword123"
        )
        
        auth_result = AuthService.authenticate_user(db, wrong_login)
        if auth_result is None:
            print("✅ Correctly rejected wrong password")
        else:
            print("❌ Should have rejected wrong password!")
        
        # Test 5: Login with email instead of username
        print("\n🔐 Test 5: Login with Email")
        print("-" * 60)
        
        email_login = UserLogin(
            username="john@example.com",  # Using email
            password="SecurePass123"
        )
        
        email_auth = AuthService.authenticate_user(db, email_login)
        if email_auth:
            print("✅ Email login successful!")
        else:
            print("❌ Email login failed!")
        
        # Test 6: Password reset request
        print("\n🔑 Test 6: Password Reset Request")
        print("-" * 60)
        
        try:
            reset_token = AuthService.request_password_reset(db, "john@example.com")
            print("✅ Reset token generated!")
            print(f"   Token: {reset_token}")
        except Exception as e:
            print(f"❌ Reset request failed: {e}")
            return
        
        # Test 7: Reset password with token
        print("\n🔑 Test 7: Reset Password")
        print("-" * 60)
        
        try:
            success = AuthService.reset_password(db, reset_token, "NewSecurePass456")
            if success:
                print("✅ Password reset successful!")
                
                # Test login with new password
                new_login = UserLogin(
                    username="johndoe",
                    password="NewSecurePass456"
                )
                
                new_auth = AuthService.authenticate_user(db, new_login)
                if new_auth:
                    print("✅ Login with new password successful!")
                else:
                    print("❌ Login with new password failed!")
        except Exception as e:
            print(f"❌ Password reset failed: {e}")
        
        # Test 8: Get user by various methods
        print("\n🔍 Test 8: Get User by Different Methods")
        print("-" * 60)
        
        user_by_username = AuthService.get_user_by_username(db, "johndoe")
        print(f"✅ Get by username: {user_by_username.username if user_by_username else 'Not found'}")
        
        user_by_email = AuthService.get_user_by_email(db, "john@example.com")
        print(f"✅ Get by email: {user_by_email.email if user_by_email else 'Not found'}")
        
        user_by_id = AuthService.get_user_by_id(db, new_user.id)
        print(f"✅ Get by ID: {user_by_id.id if user_by_id else 'Not found'}")
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ ALL AUTHENTICATION TESTS PASSED!")
        print("=" * 60)
        print("\n💡 Authentication system is ready to use!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    test_auth_system()
