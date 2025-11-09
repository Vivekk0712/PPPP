# 🧠 Planner Agent

The Planner Agent is the entry point of the AutoML pipeline. It interprets user intent using Gemini LLM and creates structured project plans in Supabase.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd agent/planner
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/service key
- `GEMINI_API_KEY`: Your Google Gemini API key

### 3. Run the Agent

```bash
python main.py
```

The service will start on `http://localhost:8001`

Or using uvicorn directly:

```bash
uvicorn main:app --reload --port 8001
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

### Handle User Message
```http
POST /agents/planner/handle_message
Content-Type: application/json

{
  "user_id": "uuid",
  "session_id": "uuid",
  "message_text": "Train a model to classify tomato leaf diseases"
}
```

**Response:**
```json
{
  "success": true,
  "project_id": "uuid",
  "message": "Project plan created successfully",
  "plan": {
    "name": "Tomato Leaf Disease Classifier",
    "task_type": "image_classification",
    "framework": "pytorch",
    "dataset_source": "kaggle",
    "search_keywords": ["tomato leaf disease", "plantvillage"],
    "preferred_model": "resnet18",
    "target_metric": "accuracy",
    "target_value": 0.9,
    "max_dataset_size_gb": 50
  }
}
```

### Get Project Details
```http
GET /agents/planner/project/{project_id}
```

## 🧪 Testing

### Manual Test with curl

```bash
# Health check
curl http://localhost:8001/health

# Create project plan
curl -X POST http://localhost:8001/agents/planner/handle_message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "session_id": "test-session-456",
    "message_text": "Train a PyTorch model for plant disease detection"
  }'
```

### Test with Python

```python
import requests

response = requests.post(
    "http://localhost:8001/agents/planner/handle_message",
    json={
        "user_id": "test-user-123",
        "session_id": "test-session-456",
        "message_text": "Train a model to classify chest X-rays"
    }
)

print(response.json())
```

## 🔄 Workflow

1. **Receive Message**: User sends natural language request via MCP Server
2. **LLM Processing**: Gemini interprets intent and generates structured plan
3. **Validation**: Pydantic validates the plan against schema
4. **Persistence**: Plan inserted into Supabase `projects` table with status `pending_dataset`
5. **User Reply**: Success message sent back via Supabase `messages` table
6. **Next Agent**: Dataset Agent picks up the project when status = `pending_dataset`

## 📊 Database Tables Used

- **projects** (insert): Store project plan
- **messages** (read/write): Chat history and replies
- **agent_logs** (insert): Debugging and audit trail
- **users** (read): Resolve user information

## 🛠️ Troubleshooting

### Gemini API Errors
- Verify your `GEMINI_API_KEY` is valid
- Check API quota limits
- Ensure internet connectivity

### Supabase Connection Issues
- Verify `SUPABASE_URL` and `SUPABASE_KEY`
- Check if tables exist (run schema from docs/README.md)
- Verify network access to Supabase

### Invalid JSON from Gemini
- The agent automatically retries with clarification
- Check `agent_logs` table for details
- Adjust prompt in `build_gemini_prompt()` if needed

## 🔐 Security Notes

- Never commit `.env` file to version control
- Use service role key only in secure environments
- Validate all user inputs before processing
- Log sensitive operations to `agent_logs`

## 📦 Integration with MCP Server

Add to MCP configuration:

```yaml
tools:
  - name: planner
    path: ./agents/planner/main.py
    port: 8001
```

## 🧩 Next Steps

After the Planner Agent creates a project:
1. Dataset Agent (Member 2) detects `status='pending_dataset'`
2. Downloads dataset from Kaggle
3. Uploads to GCP bucket
4. Updates status to `pending_training`

## 📝 Example User Interactions

**User:** "I want to build a model to detect plant diseases"

**Planner Agent Response:**
```
✅ Project created successfully!

Project Name: Plant Disease Detection Model
Task Type: image_classification
Framework: pytorch
Target Model: resnet18
Search Keywords: plant disease, plant pathology, leaf disease

📦 Next Step: Please upload your Kaggle API credentials file (kaggle.json)...
```

## 🐛 Debug Mode

Enable detailed logging:

```bash
LOG_LEVEL=DEBUG python main.py
```

Check logs in Supabase:
```sql
SELECT * FROM agent_logs 
WHERE agent_name = 'planner' 
ORDER BY created_at DESC 
LIMIT 10;
```
