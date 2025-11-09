"""
Manual testing script for Planner Agent
Run this after starting the agent to test functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test health endpoint"""
    print_section("Testing Health Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_project(message):
    """Test project creation"""
    print_section(f"Testing Project Creation: '{message}'")
    
    import uuid
    # Use the test user created in Supabase
    payload = {
        "user_id": "aa38b700-196b-4304-8adf-17334f7c4bd8",
        "session_id": str(uuid.uuid4()),
        "message_text": message
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/agents/planner/handle_message",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get("project_id")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_get_project(project_id):
    """Test getting project details"""
    print_section(f"Testing Get Project: {project_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/agents/planner/project/{project_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🧠 Planner Agent - Manual Testing Suite")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Is the agent running?")
        print("Start it with: python main.py")
        return
    
    print("\n✅ Health check passed!")
    
    # Test 2: Create projects with different messages
    test_messages = [
        "Train a model to classify tomato leaf diseases",
        "I need a PyTorch model for chest X-ray classification",
        "Build an image classifier for plant disease detection",
        "Create a model to detect cats vs dogs"
    ]
    
    project_ids = []
    for msg in test_messages:
        project_id = test_create_project(msg)
        if project_id:
            project_ids.append(project_id)
            print(f"\n✅ Project created: {project_id}")
        else:
            print(f"\n❌ Failed to create project")
    
    # Test 3: Get project details
    if project_ids:
        test_get_project(project_ids[0])
    
    # Summary
    print_section("Test Summary")
    print(f"Total projects created: {len(project_ids)}")
    print(f"Success rate: {len(project_ids)}/{len(test_messages)}")
    
    if project_ids:
        print("\n📊 Check Supabase for:")
        print("  - projects table (new entries)")
        print("  - agent_logs table (activity logs)")
        print("  - messages table (chat replies)")
        print("\n🔍 Project IDs created:")
        for pid in project_ids:
            print(f"  - {pid}")

if __name__ == "__main__":
    main()
