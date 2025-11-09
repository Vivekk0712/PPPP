"""
Test that Kaggle credentials from .env work
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_env_credentials():
    """Test if Kaggle credentials are loaded from .env"""
    print("=" * 60)
    print("Testing Kaggle Credentials from .env")
    print("=" * 60)
    
    username = os.getenv("KAGGLE_USERNAME")
    key = os.getenv("KAGGLE_KEY")
    
    print(f"\nKAGGLE_USERNAME: {username}")
    print(f"KAGGLE_KEY: {'*' * 20 if key else 'NOT SET'}")
    
    if username and key:
        print("\n✅ Kaggle credentials found in .env!")
        print("\nTesting authentication...")
        
        try:
            # Set env vars for Kaggle API
            os.environ["KAGGLE_USERNAME"] = username
            os.environ["KAGGLE_KEY"] = key
            
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            
            print("✅ Kaggle authentication successful!")
            
            # Try a quick search
            print("\nTesting dataset search...")
            datasets = api.dataset_list(search="test")[:3]
            print(f"✅ Found {len(datasets)} datasets")
            
            print("\n" + "=" * 60)
            print("✅ All tests passed!")
            print("=" * 60)
            print("\nYour agent will now use these credentials automatically")
            print("when projects don't have credentials in their metadata.")
            
        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")
            print("\nCheck that your credentials are correct in .env file")
    else:
        print("\n❌ Kaggle credentials not found in .env!")
        print("\nAdd these lines to your .env file:")
        print("KAGGLE_USERNAME=your_username")
        print("KAGGLE_KEY=your_api_key")

if __name__ == "__main__":
    test_env_credentials()
