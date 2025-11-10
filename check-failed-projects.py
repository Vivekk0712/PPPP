from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv("mcp_server/.env")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

print("\n" + "="*60)
print("🔍 CHECKING FOR FAILED PROJECTS")
print("="*60)

# Get failed projects
failed_response = supabase.table("projects").select("*").eq("status", "failed").order("created_at", desc=True).limit(5).execute()

if failed_response.data:
    print(f"\n❌ Found {len(failed_response.data)} failed project(s):\n")
    for project in failed_response.data:
        print(f"Project: {project['name']}")
        print(f"ID: {project['id']}")
        print(f"Status: {project['status']}")
        print(f"Created: {project['created_at']}")
        print(f"Updated: {project['updated_at']}")
        
        # Check if dataset exists for this project
        dataset_response = supabase.table("datasets").select("*").eq("project_id", project['id']).execute()
        if dataset_response.data:
            print(f"✅ Dataset EXISTS:")
            for ds in dataset_response.data:
                print(f"   - Name: {ds['name']}")
                print(f"   - Size: {ds['size']}")
                print(f"   - GCS URL: {ds['gcs_url']}")
        else:
            print(f"❌ No dataset found")
        
        # Get agent logs for this project
        logs_response = supabase.table("agent_logs").select("*").eq("project_id", project['id']).order("created_at", desc=True).limit(10).execute()
        if logs_response.data:
            print(f"\n📋 Recent logs:")
            for log in logs_response.data:
                print(f"   [{log['log_level']}] {log['agent_name']}: {log['message']}")
        
        print("\n" + "-"*60 + "\n")
else:
    print("\n✅ No failed projects found!\n")

print("="*60)
