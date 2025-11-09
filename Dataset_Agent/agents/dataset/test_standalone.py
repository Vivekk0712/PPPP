"""
Standalone test script for Dataset Agent
This allows you to test the agent without the MCP frontend

Usage:
1. Make sure you have kaggle.json ready
2. Run: python test_standalone.py
"""
import os
import json

def setup_kaggle_credentials():
    """
    Manually set up kaggle.json for testing
    """
    print("=== Kaggle Credentials Setup ===\n")
    print("You need your Kaggle API credentials.")
    print("Get them from: https://www.kaggle.com/settings/account → Create New API Token\n")
    
    username = input("Enter your Kaggle username: ").strip()
    key = input("Enter your Kaggle API key: ").strip()
    
    if not username or not key:
        print("❌ Both username and key are required!")
        return False
    
    # Create .kaggle directory
    kaggle_dir = os.path.expanduser("~/.kaggle")
    os.makedirs(kaggle_dir, exist_ok=True)
    
    kaggle_json_path = os.path.join(kaggle_dir, "kaggle.json")
    
    # Write credentials
    with open(kaggle_json_path, "w") as f:
        json.dump({"username": username, "key": key}, f)
    
    # Set permissions (Unix-like systems only)
    try:
        os.chmod(kaggle_json_path, 0o600)
    except Exception:
        pass  # Windows doesn't support chmod
    
    print(f"\n✅ Kaggle credentials saved to: {kaggle_json_path}")
    return True

def test_kaggle_connection():
    """
    Test if Kaggle API works
    """
    print("\n=== Testing Kaggle Connection ===\n")
    
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        
        print("✅ Kaggle authentication successful!")
        
        # Try a simple search
        print("\nTesting dataset search for 'plant disease'...")
        datasets = api.dataset_list(search="plant disease")[:3]  # Get first 3 results
        
        print(f"\n✅ Found {len(datasets)} datasets:")
        for i, ds in enumerate(datasets, 1):
            print(f"  {i}. {ds.ref}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_agent_server():
    """
    Test if the agent server is running
    """
    print("\n=== Testing Agent Server ===\n")
    
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Agent server is running!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to agent server at http://localhost:8001")
        print("   Make sure to run: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Dataset Agent - Standalone Test")
    print("=" * 60)
    
    # Step 1: Setup Kaggle credentials
    if not os.path.exists(os.path.expanduser("~/.kaggle/kaggle.json")):
        print("\n📝 Kaggle credentials not found. Let's set them up.\n")
        if not setup_kaggle_credentials():
            return
    else:
        print("\n✅ Kaggle credentials already exist at ~/.kaggle/kaggle.json")
        recreate = input("Do you want to recreate them? (y/n): ").strip().lower()
        if recreate == 'y':
            if not setup_kaggle_credentials():
                return
    
    # Step 2: Test Kaggle connection
    if not test_kaggle_connection():
        print("\n❌ Kaggle connection test failed. Please check your credentials.")
        return
    
    # Step 3: Test agent server
    test_agent_server()
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. If agent server is not running, start it with: python main.py")
    print("2. Set up your .env file with Supabase and GCP credentials")
    print("3. Use test_agent.py to test the full workflow")
    print("\nFor full integration testing, you'll need:")
    print("  - Supabase project with tables created")
    print("  - GCP bucket configured")
    print("  - A project_id from Supabase to test with")

if __name__ == "__main__":
    main()
