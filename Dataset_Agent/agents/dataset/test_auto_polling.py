"""
Test the auto-polling feature
This script helps you test the automatic dataset processing
"""
import requests
import time

BASE_URL = "http://localhost:8001"

def check_polling_status():
    """Check if auto-polling is active"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            return data.get("auto_polling", False)
        return False
    except:
        return None

def start_polling():
    """Manually start polling"""
    try:
        response = requests.post(f"{BASE_URL}/agents/dataset/polling/start")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def stop_polling():
    """Manually stop polling"""
    try:
        response = requests.post(f"{BASE_URL}/agents/dataset/polling/stop")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 60)
    print("Dataset Agent - Auto-Polling Test")
    print("=" * 60)
    
    # Check if agent is running
    print("\n1. Checking agent status...")
    status = check_polling_status()
    
    if status is None:
        print("   ❌ Agent is not running!")
        print("   Start it with: python main.py")
        return
    
    print(f"   ✅ Agent is running")
    print(f"   Auto-polling: {'✅ ACTIVE' if status else '❌ INACTIVE'}")
    
    if not status:
        print("\n2. Auto-polling is not active.")
        start = input("   Start auto-polling now? (y/n): ").strip().lower()
        if start == 'y':
            result = start_polling()
            print(f"   Result: {result}")
    
    print("\n" + "=" * 60)
    print("How Auto-Polling Works:")
    print("=" * 60)
    print("""
The agent automatically:
1. Checks Supabase every 10 seconds for projects with status='pending_dataset'
2. For each pending project:
   - Reads the search keywords
   - Searches Kaggle for matching datasets
   - Downloads the best match
   - Uploads to GCP bucket
   - Updates Supabase status to 'pending_training'
3. Logs all activity to agent_logs table

To test:
1. Make sure agent is running: python main.py
2. Add a project to Supabase with status='pending_dataset'
3. Include kaggle_credentials in the project metadata
4. Watch the agent console for [AUTO] messages
5. Check Supabase to see status change to 'pending_training'
    """)
    
    print("\nCommands:")
    print("  - Start polling: POST /agents/dataset/polling/start")
    print("  - Stop polling:  POST /agents/dataset/polling/stop")
    print("  - Check status:  GET /health")
    
    print("\nConfiguration (.env):")
    print("  - AUTO_POLL_ON_START=true    # Start polling on agent startup")
    print("  - POLL_INTERVAL_SECONDS=10   # Check every 10 seconds")

if __name__ == "__main__":
    main()
