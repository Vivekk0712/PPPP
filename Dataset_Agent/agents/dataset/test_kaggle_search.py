"""
Test Kaggle search with different keywords to find datasets
"""
import os
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

load_dotenv()

def test_search(keywords):
    """Test searching Kaggle with given keywords"""
    print(f"\n{'='*60}")
    print(f"Searching for: {' '.join(keywords)}")
    print('='*60)
    
    try:
        # Set env vars
        os.environ["KAGGLE_USERNAME"] = os.getenv("KAGGLE_USERNAME")
        os.environ["KAGGLE_KEY"] = os.getenv("KAGGLE_KEY")
        
        api = KaggleApi()
        api.authenticate()
        
        search_query = " ".join(keywords)
        datasets = api.dataset_list(search=search_query, sort_by="hottest")[:10]
        
        if datasets:
            print(f"\n✅ Found {len(datasets)} datasets:\n")
            for i, ds in enumerate(datasets, 1):
                size_bytes = ds.totalBytes if hasattr(ds, 'totalBytes') else 0
                size_gb = size_bytes / (1024**3) if size_bytes > 0 else 0
                print(f"{i}. {ds.ref}")
                print(f"   Size: {size_gb:.2f} GB")
                print(f"   Downloads: {ds.downloadCount if hasattr(ds, 'downloadCount') else 'N/A'}")
                print()
        else:
            print("❌ No datasets found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("="*60)
    print("Kaggle Dataset Search Tester")
    print("="*60)
    print("\nTesting different keyword combinations for skin cancer...\n")
    
    # Test different keyword combinations
    test_cases = [
        ["skin", "cancer"],
        ["melanoma"],
        ["skin", "lesion"],
        ["dermatology"],
        ["skin-cancer-mnist-ham10000"],
        ["ham10000"],
        ["isic", "skin"],
    ]
    
    for keywords in test_cases:
        test_search(keywords)
        input("\nPress Enter to try next search...")
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
    print("\nTo update your project in Supabase:")
    print("1. Choose keywords that returned good results")
    print("2. Run the SQL:")
    print("   UPDATE projects")
    print("   SET search_keywords = ARRAY['your', 'chosen', 'keywords']")
    print("   WHERE id = '237da916-d0cd-4350-96bb-7d49ab48b2da';")

if __name__ == "__main__":
    main()
