"""
Check if models exist in database for completed projects
"""
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv("mcp_server/.env")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

print("\n" + "="*60)
print("🔍 CHECKING MODELS IN DATABASE")
print("="*60)

# Get completed projects
projects = supabase.table("projects").select("*").eq("status", "completed").execute()

if not projects.data:
    print("\n❌ No completed projects found")
else:
    print(f"\n✅ Found {len(projects.data)} completed project(s)\n")
    
    for project in projects.data:
        print(f"📁 Project: {project['name']}")
        print(f"   ID: {project['id']}")
        print(f"   Status: {project['status']}")
        
        # Check if model exists
        models = supabase.table("models").select("*").eq("project_id", project['id']).execute()
        
        if models.data:
            print(f"   ✅ Model found:")
            for model in models.data:
                print(f"      - Name: {model['name']}")
                print(f"      - GCS URL: {model['gcs_url']}")
                print(f"      - Framework: {model['framework']}")
                print(f"      - Accuracy: {model.get('accuracy', 'N/A')}")
        else:
            print(f"   ❌ No model found in models table")
            print(f"   💡 This project needs to be trained by the Training Agent")
        
        print()

print("="*60)
