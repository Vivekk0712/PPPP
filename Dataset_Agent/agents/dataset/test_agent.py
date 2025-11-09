"""
Simple test script for Dataset Agent
Run this after setting up your .env file
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())
    return response.status_code == 200

def test_save_kaggle_auth(project_id: str, username: str, key: str):
    """Test saving Kaggle credentials"""
    payload = {
        "project_id": project_id,
        "kaggle_username": username,
        "kaggle_key": key
    }
    response = requests.post(f"{BASE_URL}/agents/dataset/auth", json=payload)
    print("Save Auth:", response.json())
    return response.status_code == 200

def test_start_dataset(project_id: str):
    """Test starting dataset job"""
    payload = {"project_id": project_id}
    response = requests.post(f"{BASE_URL}/agents/dataset/start", json=payload)
    print("Start Dataset:", response.json())
    return response.status_code == 200

def test_get_status(project_id: str):
    """Test getting status"""
    response = requests.get(f"{BASE_URL}/agents/dataset/status/{project_id}")
    print("Status:", json.dumps(response.json(), indent=2))
    return response.status_code == 200

if __name__ == "__main__":
    print("=== Dataset Agent Test ===\n")
    
    # Test health
    print("1. Testing health endpoint...")
    if test_health():
        print("✅ Health check passed\n")
    else:
        print("❌ Health check failed\n")
        exit(1)
    
    # For actual testing, you'll need a valid project_id from Supabase
    # Uncomment and fill in these values:
    
    # project_id = "your-project-uuid"
    # kaggle_username = "your-kaggle-username"
    # kaggle_key = "your-kaggle-api-key"
    
    # print("2. Testing Kaggle auth save...")
    # test_save_kaggle_auth(project_id, kaggle_username, kaggle_key)
    
    # print("\n3. Testing dataset start...")
    # test_start_dataset(project_id)
    
    # print("\n4. Testing status check...")
    # test_get_status(project_id)
    
    print("\n✅ Basic tests completed!")
    print("Uncomment the test cases above with real project_id to test full workflow")
