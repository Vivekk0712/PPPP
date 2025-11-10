"""
Test script to create a project and monitor Dataset Agent behavior
"""
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime
import time

load_dotenv("mcp_server/.env")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

print("\n" + "="*60)
print("🧪 TESTING DATASET AGENT FLOW")
print("="*60)

# Step 1: Get or create a test user
print("\n1️⃣ Getting test user...")
user_response = supabase.table("users").select("*").limit(1).execute()
if not user_response.data:
    print("❌ No users found. Please create a user first.")
    exit(1)

test_user = user_response.data[0]
user_id = test_user['id']
print(f"✅ Using user: {user_id}")

# Step 2: Create a test project
print("\n2️⃣ Creating test project...")
project_data = {
    "user_id": user_id,
    "name": "Test Flower Classification",
    "description": "Test project to verify dataset agent flow",
    "status": "pending_dataset",
    "search_keywords": ["flower", "classification"],
    "metadata": {
        "max_dataset_size_gb": 2.0
    },
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat()
}

project_response = supabase.table("projects").insert(project_data).execute()
project = project_response.data[0]
project_id = project['id']

print(f"✅ Project created: {project['name']}")
print(f"   ID: {project_id}")
print(f"   Status: {project['status']}")

# Step 3: Monitor the project
print("\n3️⃣ Monitoring project status...")
print("   (Dataset Agent should pick this up if running)")
print("   Checking every 5 seconds for 60 seconds...\n")

for i in range(12):  # Check for 60 seconds
    time.sleep(5)
    
    # Check project status
    status_response = supabase.table("projects").select("*").eq("id", project_id).execute()
    current_project = status_response.data[0]
    current_status = current_project['status']
    
    # Check if dataset exists
    dataset_response = supabase.table("datasets").select("*").eq("project_id", project_id).execute()
    has_dataset = len(dataset_response.data) > 0
    
    # Check latest log
    logs_response = supabase.table("agent_logs").select("*").eq("project_id", project_id).order("created_at", desc=True).limit(1).execute()
    latest_log = logs_response.data[0]['message'] if logs_response.data else "No logs yet"
    
    print(f"[{i*5}s] Status: {current_status} | Dataset: {'✅' if has_dataset else '❌'} | Log: {latest_log[:50]}...")
    
    if current_status == "pending_training":
        print("\n✅ SUCCESS! Project moved to pending_training")
        if has_dataset:
            dataset = dataset_response.data[0]
            print(f"   Dataset: {dataset['name']}")
            print(f"   Size: {dataset['size']}")
            print(f"   GCS URL: {dataset['gcs_url']}")
        break
    elif current_status == "failed":
        print("\n❌ FAILED! Project status is 'failed'")
        # Get all logs
        all_logs = supabase.table("agent_logs").select("*").eq("project_id", project_id).order("created_at", desc=False).execute()
        print("\n📋 All logs:")
        for log in all_logs.data:
            print(f"   [{log['log_level']}] {log['agent_name']}: {log['message']}")
        
        # Check if dataset was created despite failure
        if has_dataset:
            print("\n⚠️ IMPORTANT: Dataset EXISTS but status is FAILED!")
            dataset = dataset_response.data[0]
            print(f"   Dataset: {dataset['name']}")
            print(f"   Size: {dataset['size']}")
            print(f"   GCS URL: {dataset['gcs_url']}")
            print("\n🔍 This suggests the issue is in the status update logic!")
        break

print("\n" + "="*60)
print("Test complete!")
print("="*60)
