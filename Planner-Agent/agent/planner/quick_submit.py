"""
Quick Submit - Single command to submit a prompt
Usage: py quick_submit.py "Your prompt here"
"""

import sys
import requests
import uuid

PLANNER_URL = "http://localhost:8001"
TEST_USER_ID = "aa38b700-196b-4304-8adf-17334f7c4bd8"


def submit_prompt(prompt: str):
    """Submit a prompt to the Planner Agent"""
    payload = {
        "user_id": TEST_USER_ID,
        "session_id": str(uuid.uuid4()),
        "message_text": prompt
    }
    
    try:
        print(f"\n📝 Submitting: {prompt}")
        print("⏳ Processing with Gemini LLM...")
        
        response = requests.post(
            f"{PLANNER_URL}/agents/planner/handle_message",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"Project Name: {data['plan']['name']}")
            print(f"Project ID: {data['project_id']}")
            print(f"Task Type: {data['plan']['task_type']}")
            print(f"Framework: {data['plan']['framework']}")
            print(f"Model: {data['plan']['preferred_model']}")
            print(f"Keywords: {', '.join(data['plan']['search_keywords'])}")
            print(f"Status: pending_dataset")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"\n🔄 Dataset Agent will pick this up automatically!")
            print(f"✨ Project is now in the pipeline!\n")
            return True
        else:
            print(f"\n❌ Error {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("QUICK SUBMIT - Submit a prompt to Planner Agent")
        print("="*60)
        print("\nUsage:")
        print('  py quick_submit.py "Your prompt here"')
        print("\nExamples:")
        print('  py quick_submit.py "Train a model for plant disease detection"')
        print('  py quick_submit.py "Build a chest X-ray classifier"')
        print('  py quick_submit.py "Create a cat vs dog detector"')
        print("\n" + "="*60 + "\n")
        return
    
    prompt = " ".join(sys.argv[1:])
    submit_prompt(prompt)


if __name__ == "__main__":
    main()
