"""
Batch Process Multiple Prompts
Process multiple ML project requests at once
"""

import requests
import uuid
import time
from datetime import datetime

PLANNER_URL = "http://localhost:8001"
TEST_USER_ID = "aa38b700-196b-4304-8adf-17334f7c4bd8"

# Example prompts to process
EXAMPLE_PROMPTS = [
    "Train a model to classify tomato leaf diseases",
    "Build a chest X-ray pneumonia detector",
    "Create a cat vs dog image classifier",
    "Detect plant diseases from leaf images",
    "Classify skin cancer from dermoscopy images"
]


def process_prompt(prompt: str):
    """Process a single prompt"""
    payload = {
        "user_id": TEST_USER_ID,
        "session_id": str(uuid.uuid4()),
        "message_text": prompt
    }
    
    try:
        response = requests.post(
            f"{PLANNER_URL}/agents/planner/handle_message",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "project_id": data['project_id'],
                "name": data['plan']['name'],
                "model": data['plan']['preferred_model'],
                "keywords": data['plan']['search_keywords']
            }
        else:
            return {
                "success": False,
                "error": response.json()
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Batch process prompts"""
    print("\n" + "="*60)
    print("📦 BATCH PROCESSING MODE")
    print("="*60)
    
    # Check server health
    try:
        response = requests.get(f"{PLANNER_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Planner Agent is not running")
            return
    except:
        print("❌ Cannot connect to Planner Agent")
        print("Start it with: py main.py")
        return
    
    print(f"✅ Planner Agent is running")
    print(f"\nProcessing {len(EXAMPLE_PROMPTS)} prompts...\n")
    
    results = []
    
    for i, prompt in enumerate(EXAMPLE_PROMPTS, 1):
        print(f"\n[{i}/{len(EXAMPLE_PROMPTS)}] Processing: {prompt}")
        
        result = process_prompt(prompt)
        results.append(result)
        
        if result['success']:
            print(f"  ✅ Created: {result['name']}")
            print(f"     ID: {result['project_id']}")
            print(f"     Model: {result['model']}")
            print(f"     Keywords: {', '.join(result['keywords'][:3])}")
        else:
            print(f"  ❌ Failed: {result['error']}")
        
        # Small delay between requests
        if i < len(EXAMPLE_PROMPTS):
            time.sleep(1)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(EXAMPLE_PROMPTS)}")
    print(f"❌ Failed: {len(failed)}/{len(EXAMPLE_PROMPTS)}")
    
    if successful:
        print(f"\n📊 Created Projects:")
        for r in successful:
            print(f"  - {r['name']} ({r['project_id']})")
    
    print(f"\n🔄 All projects are now in Supabase with status='pending_dataset'")
    print(f"⏳ Dataset Agent should pick them up automatically!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
