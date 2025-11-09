"""
Planner Agent - Main Service
Handles user intent parsing and project plan creation using Gemini LLM
"""

import os
import uuid
import json
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ValidationError, Field
from supabase import create_client, Client
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Planner Agent",
    description="AutoML Planner Agent - Intent parsing and project plan creation",
    version="1.0.0"
)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Use gemini-2.5-flash for the latest stable version
model = genai.GenerativeModel('gemini-2.5-flash')


# Pydantic Models
class PlannerInput(BaseModel):
    """Input schema for planner agent"""
    user_id: str
    session_id: str
    message_text: str


class ProjectPlan(BaseModel):
    """Validated project plan schema"""
    name: str = Field(..., description="Project name")
    task_type: str = Field(default="image_classification", description="ML task type")
    framework: str = Field(default="pytorch", description="ML framework")
    dataset_source: str = Field(default="kaggle", description="Dataset source")
    search_keywords: List[str] = Field(..., description="Keywords for dataset search")
    preferred_model: str = Field(default="resnet18", description="Preferred model architecture")
    target_metric: str = Field(default="accuracy", description="Target evaluation metric")
    target_value: float = Field(default=0.9, description="Target metric value")
    max_dataset_size_gb: float = Field(default=50, description="Maximum dataset size in GB")


class PlannerResponse(BaseModel):
    """Response schema"""
    success: bool
    project_id: Optional[str] = None
    message: str
    plan: Optional[dict] = None


# Helper Functions
def get_or_create_user(firebase_uid: str) -> str:
    """Get user UUID from firebase_uid, or create if doesn't exist"""
    try:
        # Try to find existing user
        result = supabase.table("users").select("id").eq("firebase_uid", firebase_uid).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        
        # User doesn't exist, create new one
        new_user = supabase.table("users").insert({
            "firebase_uid": firebase_uid,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return new_user.data[0]["id"]
        
    except Exception as e:
        print(f"Error getting/creating user: {e}")
        raise


def log_to_supabase(project_id: Optional[str], agent_name: str, message: str, log_level: str = "info"):
    """Log agent activity to Supabase"""
    try:
        supabase.table("agent_logs").insert({
            "project_id": project_id,
            "agent_name": agent_name,
            "message": message,
            "log_level": log_level,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"Failed to log to Supabase: {e}")


def build_gemini_prompt(user_message: str) -> str:
    """Build structured prompt for Gemini LLM"""
    prompt = f"""You are a Planner Agent for an AutoML system. Convert the following user request into a structured JSON object.

User Request: "{user_message}"

You must respond with ONLY a valid JSON object (no markdown, no explanation) conforming to this exact schema:
{{
  "name": "string - A descriptive project name based on the user's request",
  "task_type": "image_classification",
  "framework": "pytorch",
  "dataset_source": "kaggle",
  "search_keywords": ["array of relevant keywords for finding datasets on Kaggle"],
  "preferred_model": "string - suggest resnet18, resnet50, or efficientnet based on task",
  "target_metric": "accuracy",
  "target_value": 0.9,
  "max_dataset_size_gb": 50
}}

Rules:
- Extract the main topic/domain from the user's message for the project name
- Generate 2-4 relevant search keywords that would help find appropriate datasets on Kaggle
- Choose an appropriate model architecture (resnet18 for simple tasks, resnet50 or efficientnet for complex ones)
- Keep target_value at 0.9 unless user specifies otherwise
- **IMPORTANT: If user mentions dataset size limit (e.g., "not more than 1GB", "under 500MB", "max 2GB"), extract that number and set max_dataset_size_gb accordingly**
  - Convert MB to GB (e.g., 500MB = 0.5GB)
  - If user says "not more than X", use X as the limit
  - If no size mentioned, use default 50GB
- Respond with ONLY the JSON object, nothing else

Examples:

Example 1 (No size limit):
User: "Train a model to classify tomato leaf diseases"
Response: {{"name": "Tomato Leaf Disease Classifier", "task_type": "image_classification", "framework": "pytorch", "dataset_source": "kaggle", "search_keywords": ["tomato leaf disease", "plantvillage", "plant pathology"], "preferred_model": "resnet18", "target_metric": "accuracy", "target_value": 0.9, "max_dataset_size_gb": 50}}

Example 2 (With size limit):
User: "Train a plant disease classifier with dataset not more than 1GB"
Response: {{"name": "Plant Disease Classifier", "task_type": "image_classification", "framework": "pytorch", "dataset_source": "kaggle", "search_keywords": ["plant disease", "leaf disease", "crop disease"], "preferred_model": "resnet18", "target_metric": "accuracy", "target_value": 0.9, "max_dataset_size_gb": 1}}

Example 3 (MB to GB conversion):
User: "Create a flower classifier, dataset under 500MB"
Response: {{"name": "Flower Classifier", "task_type": "image_classification", "framework": "pytorch", "dataset_source": "kaggle", "search_keywords": ["flower classification", "flower species", "botanical"], "preferred_model": "resnet18", "target_metric": "accuracy", "target_value": 0.9, "max_dataset_size_gb": 0.5}}

Now process this user request:
User: "Train a model to classify tomato leaf diseases"
Response: {{"name": "Tomato Leaf Disease Classifier", "task_type": "image_classification", "framework": "pytorch", "dataset_source": "kaggle", "search_keywords": ["tomato leaf disease", "plantvillage", "plant pathology"], "preferred_model": "resnet18", "target_metric": "accuracy", "target_value": 0.9, "max_dataset_size_gb": 50}}
"""
    return prompt


def parse_gemini_response(response_text: str) -> dict:
    """Parse and clean Gemini response"""
    # Remove markdown code blocks if present
    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    cleaned = cleaned.strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from Gemini: {e}")


def send_chat_reply(user_id: str, session_id: str, message: str):
    """Send reply message to user via Supabase messages table"""
    try:
        supabase.table("messages").insert({
            "user_id": user_id,
            "session_id": session_id,
            "role": "assistant",
            "content": message,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"Failed to send chat reply: {e}")


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "planner",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/agents/planner/handle_message", response_model=PlannerResponse)
async def handle_message(payload: PlannerInput):
    """
    Main endpoint for handling user messages and creating project plans
    """
    project_id = None
    
    try:
        # Log incoming request
        log_to_supabase(None, "planner", f"Received message from user {payload.user_id}", "info")
        
        # Build prompt and call Gemini
        prompt = build_gemini_prompt(payload.message_text)
        
        try:
            response = model.generate_content(prompt)
            gemini_output = response.text
        except Exception as e:
            log_to_supabase(None, "planner", f"Gemini API error: {str(e)}", "error")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"LLM service error: {str(e)}"
            )
        
        # Parse and validate response
        try:
            plan_dict = parse_gemini_response(gemini_output)
            plan = ProjectPlan(**plan_dict)
        except (ValueError, ValidationError) as e:
            log_to_supabase(None, "planner", f"Invalid LLM output: {str(e)}", "error")
            
            # Send clarification request to user
            clarification_msg = "I couldn't fully understand your request. Could you please provide more details about:\n- What type of data you want to classify\n- Any specific dataset preferences\n- Your target accuracy goals"
            send_chat_reply(payload.user_id, payload.session_id, clarification_msg)
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan generated: {str(e)}"
            )
        
        # Get or create user and insert project into Supabase
        try:
            # Get the user's UUID from firebase_uid
            user_uuid = get_or_create_user(payload.user_id)
            
            result = supabase.table("projects").insert({
                "user_id": user_uuid,
                "name": plan.name,
                "task_type": plan.task_type,
                "framework": plan.framework,
                "dataset_source": plan.dataset_source,
                "search_keywords": plan.search_keywords,
                "status": "pending_dataset",
                "metadata": plan.dict(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            
            project_id = result.data[0]["id"]
            
        except Exception as e:
            log_to_supabase(None, "planner", f"Supabase insert error: {str(e)}", "error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
        
        # Log success
        log_to_supabase(project_id, "planner", f"Project created successfully: {plan.name}", "info")
        
        # Send success message to user
        success_msg = f"""✅ Project created successfully!

**Project Name:** {plan.name}
**Task Type:** {plan.task_type}
**Framework:** {plan.framework}
**Target Model:** {plan.preferred_model}
**Search Keywords:** {', '.join(plan.search_keywords)}

📦 **Next Step:** Please upload your Kaggle API credentials file (kaggle.json) to continue with dataset discovery and download.

You can find your Kaggle API key at: https://www.kaggle.com/settings/account"""
        
        send_chat_reply(payload.user_id, payload.session_id, success_msg)
        
        return PlannerResponse(
            success=True,
            project_id=project_id,
            message="Project plan created successfully",
            plan=plan.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_to_supabase(project_id, "planner", f"Unexpected error: {str(e)}", "error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/agents/planner/project/{project_id}")
async def get_project(project_id: str):
    """Fetch project details by ID"""
    try:
        result = supabase.table("projects").select("*").eq("id", project_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
