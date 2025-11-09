"""
Verify that Dataset Agent is setting correct status
"""
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def check_project_status(project_id):
    """Check current project status"""
    print("=" * 60)
    print("Project Status Checker")
    print("=" * 60)
    
    try:
        # Get project
        response = supabase.table("projects").select("*").eq("id", project_id).execute()
        
        if not response.data:
            print(f"\n❌ Project {project_id} not found")
            return
        
        project = response.data[0]
        
        print(f"\nProject: {project['name']}")
        print(f"Status: {project['status']}")
        print(f"Updated: {project['updated_at']}")
        
        # Get recent logs
        logs = supabase.table("agent_logs").select("*").eq("project_id", project_id).order("created_at", desc=True).limit(10).execute()
        
        print(f"\nRecent Activity:")
        for log in logs.data:
            print(f"  [{log['agent_name']}] {log['message']}")
        
        # Check dataset
        dataset = supabase.table("datasets").select("*").eq("project_id", project_id).execute()
        
        if dataset.data:
            print(f"\nDataset:")
            print(f"  Name: {dataset.data[0]['name']}")
            print(f"  GCS URL: {dataset.data[0]['gcs_url']}")
            print(f"  Size: {dataset.data[0]['size']}")
        else:
            print(f"\n⚠️ No dataset found for this project")
        
        # Verify expected status
        print(f"\n{'='*60}")
        if project['status'] == 'pending_training':
            print("✅ Status is correct: 'pending_training'")
            print("   Training Agent should pick this up")
        elif project['status'] == 'training':
            print("⚠️ Status is 'training' (not 'pending_training')")
            print("   This was likely set by Training Agent")
            print("   Dataset Agent always sets 'pending_training'")
        elif project['status'] == 'pending_dataset':
            print("⚠️ Status is still 'pending_dataset'")
            print("   Dataset Agent hasn't processed this yet")
        else:
            print(f"ℹ️ Status is: '{project['status']}'")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

def check_all_statuses():
    """Check all project statuses"""
    print("\n" + "=" * 60)
    print("All Projects Status Summary")
    print("=" * 60)
    
    try:
        response = supabase.table("projects").select("id, name, status, updated_at").order("updated_at", desc=True).execute()
        
        print(f"\nTotal projects: {len(response.data)}\n")
        
        status_counts = {}
        for project in response.data:
            status = project['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            print(f"  {project['name'][:40]:40} | {status:20} | {project['updated_at'][:19]}")
        
        print(f"\nStatus Summary:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
        check_project_status(project_id)
    else:
        print("\nUsage: python verify_status_updates.py <project_id>")
        print("   Or: python verify_status_updates.py (to see all projects)\n")
        check_all_statuses()
