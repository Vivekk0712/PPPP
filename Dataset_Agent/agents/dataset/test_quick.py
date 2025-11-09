"""
Quick standalone test for Dataset Agent
Uses a small, specific dataset: puneet6060/intel-image-classification
No Supabase or GCP needed - just tests Kaggle download
"""
import os
import tempfile
from kaggle.api.kaggle_api_extended import KaggleApi

def test_kaggle_download():
    """Test downloading a specific small dataset"""
    print("=" * 60)
    print("Quick Dataset Download Test")
    print("=" * 60)
    
    # Check if kaggle.json exists
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    if not os.path.exists(kaggle_json):
        print("\n❌ Kaggle credentials not found!")
        print(f"   Expected location: {kaggle_json}")
        print("\nRun 'python test_standalone.py' first to set up credentials.")
        return False
    
    print(f"\n✅ Found Kaggle credentials at: {kaggle_json}")
    
    try:
        # Initialize Kaggle API
        print("\n1. Authenticating with Kaggle...")
        api = KaggleApi()
        api.authenticate()
        print("   ✅ Authentication successful!")
        
        # Get dataset info
        dataset_ref = "puneet6060/intel-image-classification"
        print(f"\n2. Getting info for dataset: {dataset_ref}")
        
        # Search to verify it exists
        datasets = api.dataset_list(search="intel image classification")[:5]
        print(f"   Found {len(datasets)} matching datasets:")
        for ds in datasets:
            print(f"   - {ds.ref}")
        
        # Download the dataset
        print(f"\n3. Downloading dataset: {dataset_ref}")
        print("   This may take a few minutes...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            api.dataset_download_files(dataset_ref, path=temp_dir, unzip=False)
            
            # Check what was downloaded
            files = os.listdir(temp_dir)
            if files:
                print(f"   ✅ Download successful!")
                print(f"   Downloaded files: {files}")
                
                # Get file size
                for file in files:
                    file_path = os.path.join(temp_dir, file)
                    size_bytes = os.path.getsize(file_path)
                    size_mb = size_bytes / (1024 * 1024)
                    print(f"   File: {file}")
                    print(f"   Size: {size_mb:.2f} MB")
                
                print("\n" + "=" * 60)
                print("✅ Test completed successfully!")
                print("=" * 60)
                print("\nThe agent can successfully:")
                print("  ✓ Authenticate with Kaggle")
                print("  ✓ Search for datasets")
                print("  ✓ Download datasets")
                print("\nNext: Set up Supabase and GCP to test full workflow")
                return True
            else:
                print("   ❌ No files downloaded")
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your Kaggle credentials are correct")
        print("  2. Make sure you have internet connection")
        print("  3. Verify the dataset exists: https://www.kaggle.com/datasets/puneet6060/intel-image-classification")
        return False

if __name__ == "__main__":
    test_kaggle_download()
