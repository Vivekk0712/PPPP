import os
import sys
import logging
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from tools import user_tools, chat_tools
from ai_client import generate_from_prompt
from supabase_client import init_supabase

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    PLANNER_AGENT_URL: str = "http://127.0.0.1:8001"
    DATASET_AGENT_URL: str = "http://127.0.0.1:8002"
    TRAINING_AGENT_URL: str = "http://127.0.0.1:8003"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GCP_BUCKET_NAME: str = ""

    class Config:
        env_file = ".env"

settings = Settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_supabase(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

class ChatRequest(BaseModel):
    user_id: str
    message: str
    metadata: dict | None = None
    user_name: str | None = None
    user_email: str | None = None

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/mcp/query")
async def mcp_query(request: ChatRequest):
    user_id = request.user_id
    user_message = request.message
    user_name = request.user_name
    user_email = request.user_email
    logger.info(f"Received chat request from user {user_id} (name: {user_name}, email: {user_email})")

    try:
        # 1. Get or create user profile with name/email
        logger.info("Getting/creating user profile...")
        logger.info(f"Calling get_user_profile with: firebase_uid={user_id}, email={user_email}, name={user_name}")
        user = user_tools.get_user_profile(user_id, user_email, user_name)
        logger.info(f"User profile result: {user}")

        # 2. Get chat history
        logger.info("Getting chat history...")
        chat_history = chat_tools.get_chat_history(user_id)
        logger.info(f"Chat history: {chat_history}")
        print(f"DEBUG: MCP server returning chat history: {chat_history}")

        # 3. Generate response with user context
        logger.info("Generating AI response...")
        assistant_response = generate_from_prompt(user_message, chat_history, user_name)
        logger.info(f"Assistant response generated successfully")

        # 4. Store messages
        logger.info("Storing user message...")
        chat_tools.store_message(user_id, "user", user_message)
        logger.info("Storing assistant message...")
        chat_tools.store_message(user_id, "assistant", assistant_response)
        logger.info("Messages stored successfully")

        # 5. Return response
        return {"reply": assistant_response}
    except Exception as e:
        logger.error(f"Error processing chat request for user {user_id}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/mcp/history")
async def mcp_history(user_id: str):
    logger.info(f"Fetching chat history for user {user_id}")
    try:
        chat_history = chat_tools.get_chat_history(user_id)
        return chat_history
    except Exception as e:
        logger.error(f"Error fetching chat history for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/mcp/clear-chat")
async def mcp_clear_chat(user_id: str):
    logger.info(f"Clearing chat history for user {user_id}")
    try:
        result = chat_tools.clear_chat_history(user_id)
        logger.info(f"Successfully cleared chat history for user {user_id}")
        return {"message": "Chat history cleared successfully", "result": result}
    except Exception as e:
        logger.error(f"Error clearing chat history for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============= ML Project Endpoints =============

class MLProjectRequest(BaseModel):
    user_id: str
    message: str
    user_name: str | None = None
    user_email: str | None = None

@app.post("/api/ml/planner")
async def ml_planner(request: MLProjectRequest):
    """
    Planner Agent endpoint - Creates ML project from user description
    """
    logger.info(f"ML Planner request from user {request.user_id}: {request.message}")
    
    try:
        import httpx
        
        # Call the Planner Agent service
        planner_url = settings.PLANNER_AGENT_URL
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{planner_url}/agents/planner/handle_message",
                json={
                    "user_id": request.user_id,
                    "session_id": request.user_id,  # Using user_id as session_id for now
                    "message_text": request.message
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Planner Agent error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Planner Agent error: {response.text}"
                )
            
            result = response.json()
            project_id = result.get('project_id')
            
            logger.info(f"Planner Agent created project {project_id} for user {request.user_id}")
            
            # Dataset Agent auto-polling is enabled, so no need to manually trigger
            # The agent will automatically pick up projects with status='pending_dataset'
            logger.info(f"Project {project_id} created. Dataset Agent will auto-process it.")
            
            return {
                "reply": result.get("message", "Project created successfully!"),
                "projectId": project_id,
                "status": "pending_dataset",
                "plan": result.get("plan")
            }
            
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Planner Agent: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Planner Agent service unavailable. Make sure it's running on port 8001. Error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in ML Planner: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

def get_user_uuid_from_firebase_uid(firebase_uid: str) -> str:
    """Convert Firebase UID to User UUID from database"""
    from supabase_client import get_supabase_client
    supabase = get_supabase_client()
    
    result = supabase.table("users").select("id").eq("firebase_uid", firebase_uid).execute()
    
    if result.data and len(result.data) > 0:
        return result.data[0]["id"]
    
    # User doesn't exist, create new one
    new_user = supabase.table("users").insert({
        "firebase_uid": firebase_uid
    }).execute()
    
    return new_user.data[0]["id"]


@app.get("/api/ml/projects")
async def get_ml_projects(user_id: str):
    """
    Get all ML projects for a user
    """
    logger.info(f"Fetching ML projects for user {user_id}")
    
    try:
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Convert Firebase UID to User UUID
        user_uuid = get_user_uuid_from_firebase_uid(user_id)
        
        result = supabase.table("projects").select("*").eq("user_id", user_uuid).order("created_at", desc=True).execute()
        
        projects = result.data if result.data else []
        logger.info(f"Found {len(projects)} projects for user {user_id}")
        
        return {"projects": projects}
    except Exception as e:
        logger.error(f"Error fetching ML projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/projects/{project_id}")
async def get_ml_project(project_id: str, user_id: str):
    """
    Get specific ML project details
    """
    logger.info(f"Fetching project {project_id} for user {user_id}")
    
    try:
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Convert Firebase UID to User UUID
        user_uuid = get_user_uuid_from_firebase_uid(user_id)
        
        result = supabase.table("projects").select("*").eq("id", project_id).eq("user_id", user_uuid).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = result.data[0]
        
        # Also fetch related datasets and models
        datasets = supabase.table("datasets").select("*").eq("project_id", project_id).execute()
        models = supabase.table("models").select("*").eq("project_id", project_id).execute()
        
        project["datasets"] = datasets.data if datasets.data else []
        project["models"] = models.data if models.data else []
        
        return {"project": project}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/projects/{project_id}/logs")
async def get_project_logs(project_id: str, user_id: str):
    """
    Get agent logs for a project
    """
    logger.info(f"Fetching logs for project {project_id}")
    
    try:
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Convert Firebase UID to User UUID
        user_uuid = get_user_uuid_from_firebase_uid(user_id)
        
        # Verify project belongs to user
        project = supabase.table("projects").select("id").eq("id", project_id).eq("user_id", user_uuid).execute()
        if not project.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        logs = supabase.table("agent_logs").select("*").eq("project_id", project_id).order("created_at", desc=False).execute()
        
        return {"logs": logs.data if logs.data else []}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/projects/{project_id}/download")
async def download_model(project_id: str, user_id: str):
    """
    Download trained model bundle from GCP
    """
    logger.info(f"Download request for project {project_id}")
    
    try:
        from supabase_client import get_supabase_client
        from fastapi.responses import StreamingResponse
        from google.cloud import storage
        import io
        
        supabase = get_supabase_client()
        
        # Convert Firebase UID to User UUID
        user_uuid = get_user_uuid_from_firebase_uid(user_id)
        
        # Check if user is admin
        user = supabase.table("users").select("is_admin").eq("id", user_uuid).execute()
        is_admin = user.data and user.data[0].get("is_admin", False)
        
        # Verify project and get bundle URL
        if is_admin:
            # Admin can download any project
            project = supabase.table("projects").select("*").eq("id", project_id).execute()
        else:
            # Regular user can only download their own projects
            project = supabase.table("projects").select("*").eq("id", project_id).eq("user_id", user_uuid).execute()
        
        if not project.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project.data[0]
        if project_data["status"] not in ["completed", "export_ready"]:
            raise HTTPException(status_code=400, detail="Model not ready for download. Current status: " + project_data["status"])
        
        # Get model from models table
        model = supabase.table("models").select("*").eq("project_id", project_id).execute()
        
        if not model.data:
            raise HTTPException(status_code=404, detail="No trained model found for this project")
        
        model_data = model.data[0]
        model_url = model_data.get("gcs_url")
        
        if not model_url:
            raise HTTPException(status_code=404, detail="Model GCS URL not found")
        
        # Parse GCS URL (format: gs://bucket-name/path/to/file.pth)
        if not model_url.startswith("gs://"):
            raise HTTPException(status_code=400, detail="Invalid model URL format")
        
        # Extract bucket name
        gcs_path = model_url.replace("gs://", "")
        bucket_name = gcs_path.split("/")[0]
        
        # Try to find bundle first (in exports folder)
        project_name_clean = project_data.get('name', 'model').replace(' ', '_')
        bundle_path = f"exports/{project_name_clean}_bundle.zip"
        
        logger.info(f"Checking for bundle at: {bundle_path}")
        
        # Download from GCP with explicit credentials
        gcp_credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        logger.info(f"GCP credentials path: {gcp_credentials_path}")
        
        if gcp_credentials_path and gcp_credentials_path.strip():
            logger.info(f"Using credentials from settings: {gcp_credentials_path}")
            
            if os.path.exists(gcp_credentials_path):
                logger.info("Credentials file found, using explicit authentication")
                storage_client = storage.Client.from_service_account_json(gcp_credentials_path)
            else:
                logger.error(f"Credentials file not found at: {gcp_credentials_path}")
                raise HTTPException(status_code=500, detail=f"GCP credentials file not found at: {gcp_credentials_path}")
        else:
            logger.error("GOOGLE_APPLICATION_CREDENTIALS not set in .env file")
            raise HTTPException(status_code=500, detail="GCP credentials not configured in .env file")
        
        bucket = storage_client.bucket(bucket_name)
        
        # Check if bundle exists
        bundle_blob = bucket.blob(bundle_path)
        if bundle_blob.exists():
            logger.info(f"Bundle found! Downloading: {bundle_path}")
            blob = bundle_blob
            filename = f"{project_name_clean}_bundle.zip"
            content_type = "application/zip"
        else:
            # Fallback to raw model file
            logger.info(f"Bundle not found, downloading raw model")
            model_blob_path = "/".join(gcs_path.split("/")[1:])
            blob = bucket.blob(model_blob_path)
            
            if not blob.exists():
                raise HTTPException(status_code=404, detail="Model file not found in GCP storage")
            
            filename = blob.name.split("/")[-1]
            if not filename.endswith('.pth'):
                filename = f"{project_name_clean}_model.pth"
            content_type = "application/octet-stream"
        
        # Stream the file
        file_stream = io.BytesIO()
        blob.download_to_file(file_stream)
        file_stream.seek(0)
        
        logger.info(f"Successfully downloaded: {filename}")
        
        return StreamingResponse(
            file_stream,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Full traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.post("/api/ml/projects/{project_id}/test")
async def test_model(project_id: str, user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Test model with uploaded image
    """
    logger.info(f"Test request for project {project_id}")
    
    try:
        from supabase_client import get_supabase_client
        from google.cloud import storage
        from PIL import Image
        import io
        import torch
        import torch.nn as nn
        from torchvision import models, transforms
        import json
        
        supabase = get_supabase_client()
        
        # Convert Firebase UID to User UUID
        user_uuid = get_user_uuid_from_firebase_uid(user_id)
        
        # Verify project ownership
        project = supabase.table("projects").select("*").eq("id", project_id).eq("user_id", user_uuid).execute()
        if not project.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project.data[0]
        
        # Get model info
        model_record = supabase.table("models").select("*").eq("project_id", project_id).execute()
        if not model_record.data:
            raise HTTPException(status_code=404, detail="No trained model found for this project")
        
        model_data = model_record.data[0]
        model_url = model_data.get("gcs_url")
        model_metadata = model_data.get("metadata", {})
        model_architecture = model_metadata.get("architecture", "resnet18")
        num_classes = model_metadata.get("num_classes", 2)
        
        logger.info(f"Loading model: {model_architecture} with {num_classes} classes")
        
        # Download model from GCP
        gcp_credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        if gcp_credentials_path and gcp_credentials_path.strip() and os.path.exists(gcp_credentials_path):
            storage_client = storage.Client.from_service_account_json(gcp_credentials_path)
        else:
            raise HTTPException(status_code=500, detail="GCP credentials not configured")
        
        # Parse GCS URL
        gcs_path = model_url.replace("gs://", "")
        bucket_name = gcs_path.split("/")[0]
        blob_path = "/".join(gcs_path.split("/")[1:])
        
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        # Download model to memory
        model_bytes = io.BytesIO()
        blob.download_to_file(model_bytes)
        model_bytes.seek(0)
        
        # Load model
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        
        # Create model architecture
        if model_architecture == "resnet18":
            model = models.resnet18(weights=None)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif model_architecture == "resnet34":
            model = models.resnet34(weights=None)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif model_architecture == "resnet50":
            model = models.resnet50(weights=None)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif model_architecture == "mobilenet_v2":
            model = models.mobilenet_v2(weights=None)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        elif model_architecture == "efficientnet_b0":
            model = models.efficientnet_b0(weights=None)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model architecture: {model_architecture}")
        
        # Load weights
        model.load_state_dict(torch.load(model_bytes, map_location=device))
        model.to(device)
        model.eval()
        
        # Get class labels from dataset
        dataset = supabase.table("datasets").select("*").eq("project_id", project_id).execute()
        if dataset.data:
            # Try to get labels from metadata or use generic labels
            class_labels = [f"Class_{i}" for i in range(num_classes)]
        else:
            class_labels = [f"Class_{i}" for i in range(num_classes)]
        
        # Preprocess image
        file_bytes = await file.read()
        image = Image.open(io.BytesIO(file_bytes)).convert('RGB')
        
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        img_tensor = transform(image).unsqueeze(0).to(device)
        
        # Run inference
        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        predicted_class_idx = predicted.item()
        confidence_score = confidence.item()
        
        # Get class name
        if predicted_class_idx < len(class_labels):
            predicted_class = class_labels[predicted_class_idx]
        else:
            predicted_class = f"Class_{predicted_class_idx}"
        
        logger.info(f"Prediction: {predicted_class} ({confidence_score:.2%})")
        
        return {
            "success": True,
            "prediction": predicted_class,
            "class": predicted_class,
            "confidence": confidence_score,
            "class_index": predicted_class_idx
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# Admin Endpoints
@app.get("/api/admin/stats")
async def get_admin_stats(user_id: str):
    """
    Get overall system statistics for admin dashboard
    """
    logger.info(f"Admin stats request from user {user_id}")
    
    try:
        # Check if user is admin
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Convert Firebase UID to User UUID and check admin status
        user_uuid = get_user_uuid_from_firebase_uid(user_id)
        user = supabase.table("users").select("is_admin").eq("id", user_uuid).execute()
        
        if not user.data or not user.data[0].get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        # Get counts
        users_count = supabase.table("users").select("id", count="exact").execute()
        projects_count = supabase.table("projects").select("id", count="exact").execute()
        datasets_count = supabase.table("datasets").select("id", count="exact").execute()
        models_count = supabase.table("models").select("id", count="exact").execute()
        
        # Get status breakdown
        status_breakdown = {}
        statuses = ["draft", "pending_dataset", "pending_training", "pending_evaluation", "completed", "failed"]
        for status in statuses:
            count = supabase.table("projects").select("id", count="exact").eq("status", status).execute()
            status_breakdown[status] = count.count
        
        # Get recent activity (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        recent_projects = supabase.table("projects").select("id", count="exact").gte("created_at", yesterday).execute()
        
        return {
            "total_users": users_count.count,
            "total_projects": projects_count.count,
            "total_datasets": datasets_count.count,
            "total_models": models_count.count,
            "status_breakdown": status_breakdown,
            "recent_projects_24h": recent_projects.count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching admin stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/users")
async def get_all_users(user_id: str):
    """
    Get all users with their project counts
    """
    logger.info(f"Admin users request from user {user_id}")
    
    try:
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Check if user is admin
        user_uuid = get_user_uuid_from_firebase_uid(user_id)
        user = supabase.table("users").select("is_admin").eq("id", user_uuid).execute()
        
        if not user.data or not user.data[0].get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        # Get all users
        users = supabase.table("users").select("*").order("created_at", desc=True).execute()
        
        # Get project counts for each user
        users_with_counts = []
        for user in users.data:
            projects = supabase.table("projects").select("id", count="exact").eq("user_id", user["id"]).execute()
            users_with_counts.append({
                **user,
                "project_count": projects.count
            })
        
        return {"users": users_with_counts}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/projects")
async def get_all_projects(user_id: str, limit: int = 50):
    """
    Get all projects across all users
    """
    logger.info(f"Admin projects request from user {user_id}")
    
    try:
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Check if user is admin
        user_uuid = get_user_uuid_from_firebase_uid(user_id)
        user = supabase.table("users").select("is_admin").eq("id", user_uuid).execute()
        
        if not user.data or not user.data[0].get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        # Get all projects with user info
        projects = supabase.table("projects").select("*, users(firebase_uid, email)").order("created_at", desc=True).limit(limit).execute()
        
        return {"projects": projects.data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/logs")
async def get_all_logs(user_id: str, limit: int = 100):
    """
    Get recent agent logs across all projects
    """
    logger.info(f"Admin logs request from user {user_id}")
    
    try:
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Check if user is admin
        user_uuid = get_user_uuid_from_firebase_uid(user_id)
        user = supabase.table("users").select("is_admin").eq("id", user_uuid).execute()
        
        if not user.data or not user.data[0].get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        # Get recent logs
        logs = supabase.table("agent_logs").select("*, projects(name)").order("created_at", desc=True).limit(limit).execute()
        
        return {"logs": logs.data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
