from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from google.cloud import storage
from dotenv import load_dotenv
import os
import json
import tempfile
import shutil
from datetime import datetime
import asyncio
import threading

# Load environment variables from .env file
load_dotenv()

# Don't import KaggleApi at module level to avoid auto-authentication
# Import it only when needed in the function

app = FastAPI()

# Global flag to control polling
polling_active = False

# Initialize clients
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
gcp_bucket_name = os.getenv("GCP_BUCKET_NAME")


class DatasetJobRequest(BaseModel):
    project_id: str


class KaggleAuthRequest(BaseModel):
    project_id: str
    kaggle_username: str
    kaggle_key: str


def log_to_supabase(project_id: str, message: str, level: str = "info"):
    """Log agent activity to Supabase"""
    try:
        supabase.table("agent_logs").insert({
            "project_id": project_id,
            "agent_name": "dataset",
            "message": message,
            "log_level": level,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"Failed to log to Supabase: {e}")


def send_chat_message(user_id: str, content: str):
    """Send message to user via Supabase messages table"""
    try:
        supabase.table("messages").insert({
            "user_id": user_id,
            "role": "assistant",
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"Failed to send chat message: {e}")


def authenticate_kaggle(username: str = None, key: str = None):
    """
    Authenticate Kaggle API with provided credentials or env variables
    Priority: 1. Provided params, 2. Environment variables
    """
    from kaggle.api.kaggle_api_extended import KaggleApi
    
    # Use env variables as fallback
    if not username or not key:
        username = os.getenv("KAGGLE_USERNAME")
        key = os.getenv("KAGGLE_KEY")
        print(f"Using Kaggle credentials from environment variables")
    
    if not username or not key:
        raise ValueError("Kaggle credentials not provided and not found in environment")
    
    # Set environment variables for Kaggle API
    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = key
    
    # Create temporary kaggle.json in standard Kaggle location
    # Windows: C:\Users\<username>\.kaggle\kaggle.json
    # Linux/Mac: ~/.kaggle/kaggle.json
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
    
    print(f"Kaggle credentials written to: {kaggle_json_path}")
    
    api = KaggleApi()
    api.authenticate()
    return api


def search_kaggle_dataset(api, keywords: list, max_size_gb: float = 50):
    """
    Smart search for best matching dataset on Kaggle
    Tries multiple search strategies and ranks results
    """
    if not keywords:
        print("[SEARCH] No keywords provided")
        return None
    
    # Strategy 1: Try exact phrase first
    search_query = " ".join(keywords)
    print(f"[SEARCH] Strategy 1 - Exact phrase: '{search_query}'")
    datasets = api.dataset_list(search=search_query, sort_by="hottest")[:20]
    
    # Strategy 2: If no results, try individual keywords
    if not datasets and len(keywords) > 1:
        print(f"[SEARCH] Strategy 2 - Trying individual keywords")
        for keyword in keywords:
            print(f"[SEARCH]   Trying: '{keyword}'")
            datasets = api.dataset_list(search=keyword, sort_by="hottest")[:20]
            if datasets:
                print(f"[SEARCH]   ✅ Found results with '{keyword}'")
                break
    
    # Strategy 3: Try combinations of keywords
    if not datasets and len(keywords) > 2:
        print(f"[SEARCH] Strategy 3 - Trying keyword pairs")
        for i in range(len(keywords) - 1):
            pair = f"{keywords[i]} {keywords[i+1]}"
            print(f"[SEARCH]   Trying: '{pair}'")
            datasets = api.dataset_list(search=pair, sort_by="hottest")[:20]
            if datasets:
                print(f"[SEARCH]   ✅ Found results with '{pair}'")
                break
    
    if not datasets:
        print(f"[SEARCH] ❌ No datasets found for any search strategy")
        return None
    
    print(f"[SEARCH] Found {len(datasets)} total datasets")
    
    # Smart ranking: prefer datasets with good size, downloads, and keyword match
    scored_datasets = []
    
    for dataset in datasets:
        size_bytes = dataset.totalBytes if hasattr(dataset, 'totalBytes') else 0
        size_gb = size_bytes / (1024**3) if size_bytes > 0 else 0
        downloads = dataset.downloadCount if hasattr(dataset, 'downloadCount') else 0
        ref_lower = dataset.ref.lower()
        
        # Skip if too large
        if size_gb > max_size_gb:
            continue
        
        # Skip if no size info (likely broken)
        if size_gb == 0:
            continue
        
        # Calculate score
        score = 0
        
        # Keyword relevance (highest priority)
        keyword_matches = sum(1 for kw in keywords if kw.lower() in ref_lower)
        score += keyword_matches * 100
        
        # Download popularity (medium priority)
        if downloads > 1000:
            score += 50
        elif downloads > 100:
            score += 25
        elif downloads > 10:
            score += 10
        
        # Size preference (prefer 1-10 GB, not too small, not too large)
        if 1 <= size_gb <= 10:
            score += 30
        elif 0.1 <= size_gb < 1:
            score += 15
        elif 10 < size_gb <= max_size_gb:
            score += 5
        
        scored_datasets.append({
            'dataset': dataset,
            'score': score,
            'size_gb': size_gb,
            'downloads': downloads
        })
    
    if not scored_datasets:
        print(f"[SEARCH] ❌ No suitable datasets after filtering (all too large or invalid)")
        return None
    
    # Sort by score (highest first)
    scored_datasets.sort(key=lambda x: x['score'], reverse=True)
    
    # Show top 5 candidates
    print(f"\n[SEARCH] Top candidates:")
    for i, item in enumerate(scored_datasets[:5], 1):
        ds = item['dataset']
        print(f"  {i}. {ds.ref}")
        print(f"     Score: {item['score']}, Size: {item['size_gb']:.2f} GB, Downloads: {item['downloads']}")
    
    # Return best match
    best = scored_datasets[0]
    print(f"\n[SEARCH] ✅ Selected: {best['dataset'].ref}")
    print(f"[SEARCH]    Size: {best['size_gb']:.2f} GB, Downloads: {best['downloads']}, Score: {best['score']}")
    
    return best['dataset']


def upload_to_gcp(local_path: str, destination_blob_name: str) -> str:
    """Upload file to GCP bucket"""
    client = storage.Client()
    bucket = client.bucket(gcp_bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(local_path)
    
    return f"gs://{gcp_bucket_name}/{destination_blob_name}"


@app.post("/agents/dataset/start")
async def start_dataset_job(job: DatasetJobRequest):
    """Main endpoint to start dataset discovery and upload"""
    project_id = job.project_id
    
    try:
        # Fetch project details
        log_to_supabase(project_id, "Starting dataset agent", "info")
        
        project_response = supabase.table("projects").select("*").eq("id", project_id).execute()
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = project_response.data[0]
        user_id = project["user_id"]
        keywords = project.get("search_keywords", [])
        max_size = project.get("metadata", {}).get("max_dataset_size_gb", 50)
        
        # Check if Kaggle credentials are available in project metadata or env
        kaggle_creds = project.get("metadata", {}).get("kaggle_credentials")
        
        # Authenticate Kaggle (will use env variables if not in project metadata)
        log_to_supabase(project_id, "Authenticating with Kaggle", "info")
        if kaggle_creds:
            api = authenticate_kaggle(kaggle_creds["username"], kaggle_creds["key"])
        else:
            # Use credentials from environment variables
            api = authenticate_kaggle()
        
        # Search for dataset
        log_to_supabase(project_id, f"Searching for dataset with keywords: {keywords}, max size: {max_size}GB", "info")
        send_chat_message(user_id, f"🔍 Searching for datasets (max {max_size}GB)...")
        dataset = search_kaggle_dataset(api, keywords, max_size)
        
        if not dataset:
            raise HTTPException(status_code=404, detail="No suitable dataset found")
        
        dataset_ref = dataset.ref
        log_to_supabase(project_id, f"Found dataset: {dataset_ref}", "info")
        
        # Download dataset to temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            log_to_supabase(project_id, f"Downloading dataset: {dataset_ref}", "info")
            send_chat_message(user_id, f"📦 Downloading dataset: {dataset_ref}...")
            
            api.dataset_download_files(dataset_ref, path=temp_dir, unzip=False)
            
            # Find the downloaded zip file
            downloaded_files = os.listdir(temp_dir)
            if not downloaded_files:
                raise HTTPException(status_code=500, detail="Dataset download failed")
            
            zip_file = os.path.join(temp_dir, downloaded_files[0])
            
            # Upload to GCP
            log_to_supabase(project_id, "Uploading dataset to GCP", "info")
            send_chat_message(user_id, "☁️ Uploading dataset to GCP bucket...")
            
            gcs_destination = f"raw/{dataset_ref.replace('/', '_')}.zip"
            gcs_url = upload_to_gcp(zip_file, gcs_destination)
            
            # Get file size
            file_size_bytes = os.path.getsize(zip_file)
            file_size_gb = file_size_bytes / (1024**3)
        
        # Record in Supabase datasets table
        log_to_supabase(project_id, "Recording dataset metadata in Supabase", "info")
        print(f"📝 Storing dataset info in Supabase...")
        dataset_stored = False
        try:
            dataset_result = supabase.table("datasets").insert({
                "project_id": project_id,
                "name": dataset_ref,
                "gcs_url": gcs_url,
                "size": f"{file_size_gb:.2f} GB",
                "source": "kaggle",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            print(f"✅ Dataset info stored successfully")
            dataset_stored = True
        except Exception as dataset_error:
            print(f"❌ Failed to store dataset info: {dataset_error}")
            import traceback
            print(traceback.format_exc())
            log_to_supabase(project_id, f"Failed to store dataset info: {str(dataset_error)}", "error")
            raise
        
        # Update project status - this is critical, retry if needed
        print(f"📝 Updating project status to pending_training...")
        status_updated = False
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                update_result = supabase.table("projects").update({
                    "status": "pending_training",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", project_id).execute()
                print(f"✅ Project status updated successfully (attempt {attempt + 1})")
                status_updated = True
                break
            except Exception as update_error:
                print(f"⚠️ Failed to update project status (attempt {attempt + 1}/{max_retries}): {update_error}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # Wait 2 seconds before retry
                else:
                    # Last attempt failed
                    print(f"❌ All {max_retries} attempts to update status failed")
                    log_to_supabase(project_id, f"Dataset uploaded but status update failed: {str(update_error)}", "warning")
                    # Don't raise - dataset is uploaded, we can manually fix status later
                    send_chat_message(user_id, 
                        f"⚠️ Dataset uploaded successfully but status update failed.\n"
                        f"Dataset: {dataset_ref}\n"
                        f"Size: {file_size_gb:.2f} GB\n"
                        f"Please contact support to update project status.")
        
        if not status_updated:
            # Dataset is uploaded but status wasn't updated - this is not a complete failure
            print(f"⚠️ Dataset uploaded successfully but status remains 'pending_dataset'")
            print(f"   Manual intervention may be needed to update status to 'pending_training'")
            # Don't raise exception - the dataset work is done
        
        log_to_supabase(project_id, "Dataset agent completed successfully", "info")
        print(f"✅ Dataset agent completed successfully!")
        send_chat_message(user_id, 
            f"✅ Dataset uploaded successfully!\n"
            f"Dataset: {dataset_ref}\n"
            f"Size: {file_size_gb:.2f} GB\n"
            f"Training Agent can now begin.")
        
        # Clean up Kaggle credentials after use for security
        kaggle_json_path = os.path.expanduser("~/.kaggle/kaggle.json")
        if os.path.exists(kaggle_json_path):
            os.remove(kaggle_json_path)
            print(f"Cleaned up Kaggle credentials from: {kaggle_json_path}")
        
        return {
            "success": True,
            "dataset_name": dataset_ref,
            "gcs_url": gcs_url,
            "size": f"{file_size_gb:.2f} GB"
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERROR in Dataset Agent: {str(e)}")
        print(f"Full traceback:\n{error_details}")
        
        log_to_supabase(project_id, f"Error: {str(e)}", "error")
        
        # Check if dataset was already uploaded before marking as failed
        try:
            dataset_check = supabase.table("datasets").select("*").eq("project_id", project_id).execute()
            if dataset_check.data:
                # Dataset exists, don't mark as failed
                print(f"⚠️ Error occurred but dataset was uploaded. Not marking as failed.")
                log_to_supabase(project_id, "Dataset uploaded but error in post-processing", "warning")
                # Return partial success
                dataset = dataset_check.data[0]
                return {
                    "success": True,
                    "dataset_name": dataset['name'],
                    "gcs_url": dataset['gcs_url'],
                    "size": dataset['size'],
                    "warning": "Dataset uploaded but status update may have failed"
                }
            else:
                # No dataset, this is a real failure
                supabase.table("projects").update({
                    "status": "failed",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", project_id).execute()
                print(f"❌ Marked project as failed (no dataset found)")
        except Exception as check_error:
            # If we can't check, mark as failed to be safe
            print(f"⚠️ Could not check dataset status: {check_error}")
            supabase.table("projects").update({
                "status": "failed",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", project_id).execute()
        
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/dataset/auth")
async def save_kaggle_auth(auth: KaggleAuthRequest):
    """Save Kaggle credentials to project metadata"""
    try:
        project_response = supabase.table("projects").select("*").eq("id", auth.project_id).execute()
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = project_response.data[0]
        metadata = project.get("metadata", {})
        metadata["kaggle_credentials"] = {
            "username": auth.kaggle_username,
            "key": auth.kaggle_key
        }
        
        supabase.table("projects").update({
            "metadata": metadata,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", auth.project_id).execute()
        
        log_to_supabase(auth.project_id, "Kaggle credentials saved", "info")
        
        return {"success": True, "message": "Kaggle credentials saved"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/dataset/status/{project_id}")
async def get_status(project_id: str):
    """Get dataset agent status for a project"""
    try:
        # Get dataset info
        dataset_response = supabase.table("datasets").select("*").eq("project_id", project_id).execute()
        
        # Get logs
        logs_response = supabase.table("agent_logs").select("*").eq("project_id", project_id).eq("agent_name", "dataset").order("created_at", desc=True).limit(10).execute()
        
        return {
            "dataset": dataset_response.data[0] if dataset_response.data else None,
            "logs": logs_response.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "dataset",
        "auto_polling": polling_active
    }


@app.post("/agents/dataset/polling/start")
async def start_polling():
    """Start automatic polling for pending_dataset projects"""
    global polling_active
    if polling_active:
        return {"success": False, "message": "Polling already active"}
    
    polling_active = True
    # Start polling in background thread
    thread = threading.Thread(target=poll_pending_projects, daemon=True)
    thread.start()
    
    return {"success": True, "message": "Auto-polling started"}


@app.post("/agents/dataset/polling/stop")
async def stop_polling():
    """Stop automatic polling"""
    global polling_active
    polling_active = False
    return {"success": True, "message": "Auto-polling stopped"}


def process_project_sync(project_id: str):
    """
    Synchronous version of dataset processing for background thread
    """
    try:
        print(f"\n[AUTO] Processing project: {project_id}")
        log_to_supabase(project_id, "Auto-processing started by polling agent", "info")
        
        # Fetch project details
        project_response = supabase.table("projects").select("*").eq("id", project_id).execute()
        if not project_response.data:
            print(f"[AUTO] Project {project_id} not found")
            return
        
        project = project_response.data[0]
        user_id = project["user_id"]
        keywords = project.get("search_keywords", [])
        max_size = project.get("metadata", {}).get("max_dataset_size_gb", 50)
        
        # Check Kaggle credentials (use env as fallback)
        kaggle_creds = project.get("metadata", {}).get("kaggle_credentials")
        
        # Authenticate Kaggle (will use env variables if not in project metadata)
        log_to_supabase(project_id, "Authenticating with Kaggle", "info")
        if kaggle_creds:
            api = authenticate_kaggle(kaggle_creds["username"], kaggle_creds["key"])
        else:
            # Use credentials from environment variables
            print(f"[AUTO] Using Kaggle credentials from .env file")
            api = authenticate_kaggle()
        
        # Search for dataset
        log_to_supabase(project_id, f"Searching for dataset with keywords: {keywords}", "info")
        dataset = search_kaggle_dataset(api, keywords, max_size)
        
        if not dataset:
            log_to_supabase(project_id, "No suitable dataset found", "error")
            print(f"[AUTO] No dataset found for project {project_id}")
            return
        
        dataset_ref = dataset.ref
        log_to_supabase(project_id, f"Found dataset: {dataset_ref}", "info")
        print(f"[AUTO] Found dataset: {dataset_ref}")
        
        # Download dataset
        with tempfile.TemporaryDirectory() as temp_dir:
            log_to_supabase(project_id, f"Downloading dataset: {dataset_ref}", "info")
            send_chat_message(user_id, f"📦 Auto-downloading dataset: {dataset_ref}...")
            
            api.dataset_download_files(dataset_ref, path=temp_dir, unzip=False)
            
            downloaded_files = os.listdir(temp_dir)
            if not downloaded_files:
                log_to_supabase(project_id, "Dataset download failed", "error")
                return
            
            zip_file = os.path.join(temp_dir, downloaded_files[0])
            
            # Upload to GCP
            log_to_supabase(project_id, "Uploading dataset to GCP", "info")
            send_chat_message(user_id, "☁️ Uploading dataset to GCP bucket...")
            
            gcs_destination = f"raw/{dataset_ref.replace('/', '_')}.zip"
            gcs_url = upload_to_gcp(zip_file, gcs_destination)
            
            file_size_bytes = os.path.getsize(zip_file)
            file_size_gb = file_size_bytes / (1024**3)
        
        # Record in Supabase
        log_to_supabase(project_id, "Recording dataset metadata in Supabase", "info")
        print(f"[AUTO] 📝 Storing dataset info in Supabase...")
        dataset_stored = False
        try:
            supabase.table("datasets").insert({
                "project_id": project_id,
                "name": dataset_ref,
                "gcs_url": gcs_url,
                "size": f"{file_size_gb:.2f} GB",
                "source": "kaggle",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            print(f"[AUTO] ✅ Dataset info stored successfully")
            dataset_stored = True
        except Exception as dataset_error:
            print(f"[AUTO] ❌ Failed to store dataset info: {dataset_error}")
            import traceback
            print(f"[AUTO] Traceback: {traceback.format_exc()}")
            log_to_supabase(project_id, f"Failed to store dataset info: {str(dataset_error)}", "error")
            raise
        
        # Update project status - retry logic for robustness
        print(f"[AUTO] 📝 Updating project status to pending_training...")
        status_updated = False
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                update_result = supabase.table("projects").update({
                    "status": "pending_training",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", project_id).execute()
                print(f"[AUTO] ✅ Status updated successfully (attempt {attempt + 1}): {update_result.data}")
                status_updated = True
                break
            except Exception as status_error:
                print(f"[AUTO] ⚠️ Failed to update status (attempt {attempt + 1}/{max_retries}): {status_error}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # Wait 2 seconds before retry
                else:
                    # Last attempt failed
                    print(f"[AUTO] ❌ All {max_retries} attempts to update status failed")
                    import traceback
                    print(f"[AUTO] Traceback: {traceback.format_exc()}")
                    log_to_supabase(project_id, f"Dataset uploaded but status update failed: {str(status_error)}", "warning")
                    # Don't raise - dataset is uploaded successfully
                    send_chat_message(user_id, 
                        f"⚠️ Dataset uploaded successfully but status update failed.\n"
                        f"Dataset: {dataset_ref}\n"
                        f"Size: {file_size_gb:.2f} GB\n"
                        f"Please contact support to update project status.")
        
        if not status_updated:
            # Dataset is uploaded but status wasn't updated
            print(f"[AUTO] ⚠️ Dataset uploaded successfully but status remains 'pending_dataset'")
            print(f"[AUTO]    Manual intervention may be needed")
            # Don't raise exception - the dataset work is done
            return
        
        log_to_supabase(project_id, "Auto-processing completed successfully", "info")
        send_chat_message(user_id, 
            f"✅ Dataset auto-uploaded successfully!\n"
            f"Dataset: {dataset_ref}\n"
            f"Size: {file_size_gb:.2f} GB\n"
            f"Training Agent can now begin.")
        
        print(f"[AUTO] ✅ Project {project_id} completed successfully")
        
        # Cleanup
        kaggle_json_path = os.path.expanduser("~/.kaggle/kaggle.json")
        if os.path.exists(kaggle_json_path):
            os.remove(kaggle_json_path)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[AUTO] ❌ Error processing project {project_id}: {e}")
        print(f"[AUTO] Traceback:\n{error_details}")
        
        log_to_supabase(project_id, f"Auto-processing error: {str(e)}", "error")
        
        # Check if dataset was already uploaded before marking as failed
        try:
            dataset_check = supabase.table("datasets").select("*").eq("project_id", project_id).execute()
            if dataset_check.data:
                # Dataset exists, don't mark as failed
                print(f"[AUTO] ⚠️ Error occurred but dataset was uploaded. Not marking as failed.")
                log_to_supabase(project_id, "Dataset uploaded but error in post-processing", "warning")
            else:
                # No dataset, this is a real failure
                supabase.table("projects").update({
                    "status": "failed",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", project_id).execute()
                print(f"[AUTO] ❌ Marked project as failed (no dataset found)")
        except Exception as check_error:
            # If we can't check, mark as failed to be safe
            print(f"[AUTO] ⚠️ Could not check dataset status: {check_error}")
            supabase.table("projects").update({
                "status": "failed",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", project_id).execute()


def poll_pending_projects():
    """
    Background thread that polls Supabase for pending_dataset projects
    """
    global polling_active
    print("\n" + "="*60)
    print("🤖 AUTO-POLLING STARTED")
    print("="*60)
    print("Watching for projects with status='pending_dataset'")
    print("Press Ctrl+C to stop the agent\n")
    
    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "10"))
    
    while polling_active:
        try:
            # Query for pending projects
            response = supabase.table("projects").select("*").eq("status", "pending_dataset").execute()
            
            if response.data:
                print(f"[AUTO] Found {len(response.data)} pending project(s)")
                
                for project in response.data:
                    project_id = project["id"]
                    project_name = project.get("name", "Unknown")
                    
                    print(f"[AUTO] Processing: {project_name} ({project_id})")
                    
                    # Process the project
                    process_project_sync(project_id)
            
            # Wait before next poll
            import time
            time.sleep(poll_interval)
            
        except KeyboardInterrupt:
            print("\n[AUTO] Polling stopped by user")
            polling_active = False
            break
        except Exception as e:
            print(f"[AUTO] Polling error: {e}")
            import time
            time.sleep(poll_interval)
    
    print("[AUTO] Polling stopped")


if __name__ == "__main__":
    import uvicorn
    
    # Check if auto-polling should start on startup
    auto_start = os.getenv("AUTO_POLL_ON_START", "true").lower() == "true"
    
    if auto_start:
        # Start polling in background thread
        polling_active = True
        poll_thread = threading.Thread(target=poll_pending_projects, daemon=True)
        poll_thread.start()
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8002)
