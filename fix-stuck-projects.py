"""
Utility script to fix projects that are marked as 'failed' 
but have successfully uploaded datasets
"""
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv("mcp_server/.env")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

print("\n" + "="*60)
print("🔧 FIXING STUCK PROJECTS")
print("="*60)

# Find failed projects that have datasets
print("\n1️⃣ Searching for failed projects with uploaded datasets...")

failed_projects = supabase.table("projects").select("*").eq("status", "failed").execute()

if not failed_projects.data:
    print("✅ No failed projects found!")
    exit(0)

print(f"Found {len(failed_projects.data)} failed project(s)")

fixed_count = 0
no_dataset_count = 0

for project in failed_projects.data:
    project_id = project['id']
    project_name = project['name']
    
    print(f"\n📋 Checking: {project_name}")
    print(f"   ID: {project_id}")
    
    # Check if dataset exists
    dataset_response = supabase.table("datasets").select("*").eq("project_id", project_id).execute()
    
    if dataset_response.data:
        # Dataset exists! Fix the status
        dataset = dataset_response.data[0]
        print(f"   ✅ Dataset found: {dataset['name']}")
        print(f"   📦 Size: {dataset['size']}")
        print(f"   ☁️ GCS URL: {dataset['gcs_url']}")
        
        # Update status to pending_training
        print(f"   🔧 Fixing status: failed → pending_training")
        
        try:
            supabase.table("projects").update({
                "status": "pending_training",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", project_id).execute()
            
            # Log the fix
            supabase.table("agent_logs").insert({
                "project_id": project_id,
                "agent_name": "system",
                "message": "Status fixed: Dataset was uploaded but project was marked as failed",
                "log_level": "info",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            print(f"   ✅ Status fixed successfully!")
            fixed_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed to fix status: {e}")
    else:
        # No dataset - this is a legitimate failure
        print(f"   ❌ No dataset found - this is a legitimate failure")
        no_dataset_count += 1

print("\n" + "="*60)
print("📊 SUMMARY")
print("="*60)
print(f"✅ Fixed: {fixed_count} project(s)")
print(f"❌ Legitimate failures: {no_dataset_count} project(s)")
print("="*60)

if fixed_count > 0:
    print("\n💡 TIP: These projects can now be picked up by the Training Agent")
    print("   (once Training Agent is integrated)")
