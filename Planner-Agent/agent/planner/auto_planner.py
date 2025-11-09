"""
Automated Planner Agent - Continuous Processing
Monitors for new user messages and automatically creates project plans
"""

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
PLANNER_URL = "http://localhost:8001"
TEST_USER_ID = "aa38b700-196b-4304-8adf-17334f7c4bd8"  # Test user we created
CHECK_INTERVAL = 5  # seconds

def create_project_from_prompt(prompt: str):
    """Send prompt to Planner Agent and create project"""
    import uuid
    
    payload = {
        "user_id": TEST_USER_ID,
        "session_id": str(uuid.uuid4()),
        "message_text": prompt
    }
    
    try:
        print(f"\n{'='*60}")
        print(f"📝 Processing Prompt: {prompt}")
        print(f"{'='*60}")
        
        response = requests.post(
            f"{PLANNER_URL}/agents/planner/handle_message",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Project Created")
            print(f"   Project ID: {data['project_id']}")
            print(f"   Name: {data['plan']['name']}")
            print(f"   Model: {data['plan']['preferred_model']}")
            print(f"   Keywords: {', '.join(data['plan']['search_keywords'])}")
            print(f"   Status: pending_dataset (ready for Dataset Agent)")
            print(f"\n🔄 Dataset Agent (architecture2.md) should pick this up automatically!")
            return data['project_id']
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def main():
    """Main automation loop"""
    print("\n" + "="*60)
    print("🤖 AUTOMATED PLANNER AGENT")
    print("="*60)
    print(f"Planner URL: {PLANNER_URL}")
    print(f"User ID: {TEST_USER_ID}")
    print("="*60)
    
    # Check if server is running
    try:
        response = requests.get(f"{PLANNER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Planner Agent is running")
        else:
            print("❌ Planner Agent health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Planner Agent: {e}")
        print("\nPlease start the agent first:")
        print("  py main.py")
        return
    
    print("\n" + "="*60)
    print("AUTOMATION MODE")
    print("="*60)
    print("Enter your prompts below. Each prompt will be:")
    print("  1. Sent to Gemini LLM for intent parsing")
    print("  2. Validated and structured")
    print("  3. Stored in Supabase with status='pending_dataset'")
    print("  4. Picked up by Dataset Agent automatically")
    print("\nType 'quit' or 'exit' to stop")
    print("="*60 + "\n")
    
    while True:
        try:
            # Get user input
            prompt = input("💬 Enter your prompt: ").strip()
            
            if not prompt:
                continue
                
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Stopping automation...")
                break
            
            # Process the prompt
            project_id = create_project_from_prompt(prompt)
            
            if project_id:
                print(f"\n✨ Project {project_id} is now in the pipeline!")
                print(f"⏳ Waiting for Dataset Agent to process...")
            
            print("\n" + "-"*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Stopping automation...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
