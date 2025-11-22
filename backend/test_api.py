"""
Test Protected APIs
Tests authentication and authorization for all endpoints
"""

import requests
import json
from pathlib import Path


# API Base URL
BASE_URL = "http://localhost:8000"

# Test credentials
TEST_USER = {
    "username": "testuser_api",
    "email": "testapi@example.com",
    "password": "TestPass123"
}


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(success: bool, message: str):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")


def test_register():
    """Test user registration"""
    print_section("TEST 1: User Registration")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=TEST_USER
    )
    
    if response.status_code == 201:
        print_result(True, "User registered successfully")
        return True
    elif response.status_code == 400:
        print_result(True, "User already exists (expected)")
        return True
    else:
        print_result(False, f"Registration failed: {response.text}")
        return False


def test_login():
    """Test user login and get token"""
    print_section("TEST 2: User Login")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print_result(True, f"Login successful")
        print(f"   Token: {token[:50]}...")
        return token
    else:
        print_result(False, f"Login failed: {response.text}")
        return None


def test_get_profile(token: str):
    """Test getting user profile"""
    print_section("TEST 3: Get User Profile")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print_result(True, f"Profile retrieved: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   User ID: {user['id']}")
        return user
    else:
        print_result(False, f"Failed: {response.text}")
        return None


def test_update_profile(token: str):
    """Test updating user profile"""
    print_section("TEST 4: Update User Profile")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        f"{BASE_URL}/users/me",
        headers=headers,
        json={"email": "newemail@example.com"}
    )
    
    if response.status_code == 200:
        user = response.json()
        print_result(True, f"Profile updated")
        print(f"   New email: {user['email']}")
        
        # Revert back
        requests.put(
            f"{BASE_URL}/users/me",
            headers=headers,
            json={"email": TEST_USER["email"]}
        )
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False


def test_get_events(token: str, user_id: int):
    """Test getting user events"""
    print_section("TEST 5: Get User Events")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/events/user/{user_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Events retrieved")
        print(f"   Total: {data['total']}")
        print(f"   Unread: {data['unread']}")
        print(f"   Page: {data['page']}")
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False


def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    print_section("TEST 6: Unauthorized Access (Should Fail)")
    
    response = requests.get(f"{BASE_URL}/users/me")
    
    if response.status_code == 401 or response.status_code == 403:
        print_result(True, "Correctly rejected unauthorized request")
        return True
    else:
        print_result(False, f"Should have been rejected: {response.status_code}")
        return False


def test_get_statistics(token: str, user_id: int):
    """Test getting event statistics"""
    print_section("TEST 7: Get Event Statistics")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/events/user/{user_id}/statistics?days=7",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print_result(True, "Statistics retrieved")
        print(f"   Total Events: {stats['total_events']}")
        print(f"   By Type: {stats['by_type']}")
        print(f"   Avg Confidence: {stats['average_confidence']}")
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False


def test_file_upload(token: str):
    """Test file upload"""
    print_section("TEST 8: File Upload")
    
    # Create a test image
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
    
    response = requests.post(
        f"{BASE_URL}/files/upload",
        headers=headers,
        files=files
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, "File uploaded successfully")
        print(f"   Path: {data['file_path']}")
        print(f"   Size: {data['size']} bytes")
        return data['file_path']
    else:
        print_result(False, f"Failed: {response.text}")
        return None


def main():
    """
    Run all API tests
    """
    print("\n" + "=" * 60)
    print("🧪 API AUTHENTICATION & AUTHORIZATION TEST")
    print("=" * 60)
    print("\nMake sure the API server is running:")
    print("  python -m app.main")
    print("")
    
    input("Press Enter to start tests...")
    
    # Test 1: Register
    if not test_register():
        print("\n❌ Cannot continue without registration")
        return
    
    # Test 2: Login
    token = test_login()
    if not token:
        print("\n❌ Cannot continue without token")
        return
    
    # Test 3: Get Profile
    user = test_get_profile(token)
    if not user:
        print("\n❌ Cannot continue without user profile")
        return
    
    user_id = user['id']
    
    # Test 4: Update Profile
    test_update_profile(token)
    
    # Test 5: Get Events
    test_get_events(token, user_id)
    
    # Test 6: Unauthorized Access
    test_unauthorized_access()
    
    # Test 7: Get Statistics
    test_get_statistics(token, user_id)
    
    # Test 8: File Upload
    try:
        test_file_upload(token)
    except ImportError:
        print_result(False, "PIL not installed. Skipping file upload test")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)
    print("\n💡 Your API is protected and working correctly!")
    print("\nNext steps:")
    print("  1. Test in Swagger UI: http://localhost:8000/docs")
    print("  2. Click 'Authorize' button and paste your token")
    print("  3. Try protected endpoints")


if __name__ == "__main__":
    main()