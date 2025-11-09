"""
Full workflow test for Dataset Agent with Supabase
Requires: Supabase tables set up (run supabase_setup.sql first)
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

# Test project ID from supabase_setup.sql
TEST_PROJECT_ID = "11111111-1111-1111-1111-111111111111"

def test_full_workflow():
    """Test the complete dataset agent workflow"""
    print("=" * 60)
    print("Dataset Agent - Full Workflow Test")
    print("=" * 60)
    
    # Step 1: Check agent health
    print("\n1. Checking agent health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"   ✅ Agent is healthy: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to agent: {e}")
        print("   Make sure to run: python main.py")
        return
    
    # Step 2: Save Kaggle credentials (if needed)
    print("\n2. Saving Kaggle credentials to project...")
    kaggle_username = input("   Enter your Kaggle username: ").strip()
    kaggle_key = input("   Enter your Kaggle API key: ").strip()
    
    if kaggle_username and kaggle_key:
        try:
            response = requests.post(
                f"{BASE_URL}/agents/dataset/auth",
                json={
                    "project_id": TEST_PROJECT_ID,
                    "kaggle_username": kaggle_username,
                    "kaggle_key": kaggle_key
                }
            )
            if response.status_code == 200:
                print(f"   ✅ Credentials saved: {response.json()}")
            else:
                print(f"   ❌ Failed to save credentials: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
    else:
        print("   ⚠️  Skipping credential save (assuming already in Supabase)")
    
    # Step 3: Start dataset job
    print("\n3. Starting dataset discovery and upload...")
    print("   This will:")
    print("   - Search Kaggle for 'intel image classification'")
    print("   - Download the dataset")
    print("   - Upload to GCP bucket")
    print("   - Update Supabase")
    
    confirm = input("\n   Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("   Cancelled.")
        return
    
    try:
        response = requests.post(
            f"{BASE_URL}/agents/dataset/start",
            json={"project_id": TEST_PROJECT_ID}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n   ✅ Dataset job completed successfully!")
            print(f"   Dataset: {result.get('dataset_name')}")
            print(f"   GCS URL: {result.get('gcs_url')}")
            print(f"   Size: {result.get('size')}")
        else:
            print(f"\n   ❌ Job failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        return
    
    # Step 4: Check status
    print("\n4. Checking final status...")
    time.sleep(1)
    
    try:
        response = requests.get(f"{BASE_URL}/agents/dataset/status/{TEST_PROJECT_ID}")
        if response.status_code == 200:
            status = response.json()
            print("\n   Dataset Info:")
            print(json.dumps(status.get('dataset'), indent=4))
            print("\n   Recent Logs:")
            for log in status.get('logs', [])[:5]:
                print(f"   [{log['log_level']}] {log['message']}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Full workflow test completed!")
    print("=" * 60)
    print("\nCheck your Supabase tables:")
    print("  - datasets: Should have new entry")
    print("  - agent_logs: Should have activity logs")
    print("  - projects: Status should be 'pending_training'")
    print("\nCheck your GCP bucket:")
    print("  - Should have file in raw/ folder")

if __name__ == "__main__":
    print("\n⚠️  Prerequisites:")
    print("  1. Run supabase_setup.sql in your Supabase SQL Editor")
    print("  2. Make sure .env file has correct Supabase and GCP credentials")
    print("  3. Start the agent: python main.py")
    print("  4. Have your Kaggle credentials ready")
    
    proceed = input("\nAll prerequisites met? (y/n): ").strip().lower()
    if proceed == 'y':
        test_full_workflow()
    else:
        print("\nPlease complete prerequisites first.")
