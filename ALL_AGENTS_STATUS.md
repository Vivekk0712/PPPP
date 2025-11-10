# All Agents Status & Quick Reference

## Agent Overview

| Agent | Port | Status | Auto-Polling | Purpose |
|-------|------|--------|--------------|---------|
| **Backend** | 4000 | ✅ Ready | N/A | API Gateway, Authentication |
| **Frontend** | 5173 | ✅ Ready | Auto-refresh (5s) | User Interface |
| **MCP Server** | 8000 | ✅ Ready | N/A | Agent Orchestration |
| **Planner Agent** | 8001 | ✅ Ready | No | Parse user intent, create projects |
| **Dataset Agent** | 8002 | ✅ Ready | Yes (10s) | Search & download datasets |
| **Training Agent** | 8003 | ✅ Ready | Yes (10s) | Train & evaluate models |

## Status Flow

```
User Message
    ↓
Planner Agent (8001)
    ↓ Creates project
    status: pending_dataset
    ↓
Dataset Agent (8002) [Auto-polls every 10s]
    ↓ Downloads dataset
    status: pending_training
    ↓
Training Agent (8003) [Auto-polls every 10s]
    ↓ Trains model
    status: pending_evaluation
    ↓
Training Agent (8003) [Auto-polls every 10s]
    ↓ Evaluates model
    status: completed
    ↓
User downloads bundle
```

## Quick Start Commands

### Start All Services (Windows)

```bash
# Terminal 1 - Backend
cd backend
npm start

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - MCP Server
cd mcp_server
python main.py

# Terminal 4 - Planner Agent
cd Planner-Agent/agent/planner
python main.py

# Terminal 5 - Dataset Agent
cd Dataset_Agent/agents/dataset
python main.py

# Terminal 6 - Training Agent
cd Trainer-Agent/agent
python main.py
```

### Or Use Batch Scripts

```bash
# Start each in separate terminal
start-backend.bat
start-frontend.bat
start-mcp-server.bat
start-planner-agent.bat
start-dataset-agent.bat
start-training-agent.bat
```

## Health Checks

```bash
# Backend
curl http://localhost:4000/health

# MCP Server
curl http://localhost:8000/health

# Planner Agent
curl http://localhost:8001/health

# Dataset Agent
curl http://localhost:8002/health

# Training Agent
curl http://localhost:8003/health
```

## Environment Files

### Backend (.env)
```bash
PORT=4000
MCP_SERVER_URL=http://localhost:8000
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/firebase-key.json
```

### MCP Server (.env)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-key
GEMINI_API_KEY=your-key
PLANNER_AGENT_URL=http://127.0.0.1:8001
DATASET_AGENT_URL=http://127.0.0.1:8002
TRAINING_AGENT_URL=http://127.0.0.1:8003
```

### Planner Agent (.env)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key
GEMINI_API_KEY=your-key
```

### Dataset Agent (.env)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key
GCP_BUCKET_NAME=your-bucket
KAGGLE_USERNAME=your-username
KAGGLE_KEY=your-key
GOOGLE_APPLICATION_CREDENTIALS=path/to/gcp-key.json
```

### Training Agent (.env)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key
GCP_BUCKET_NAME=your-bucket
GOOGLE_APPLICATION_CREDENTIALS=path/to/gcp-key.json
LOG_LEVEL=INFO
BATCH_SIZE=64
DEFAULT_EPOCHS=10
DEFAULT_LEARNING_RATE=0.001
```

## Database Tables

### projects
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `name` (TEXT) - Project name
- `description` (TEXT) - Project description
- `status` (TEXT) - Current status
- `task_type` (TEXT) - ML task type
- `framework` (TEXT) - ML framework
- `search_keywords` (TEXT[]) - Keywords for dataset search
- `metadata` (JSONB) - Additional metadata
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### datasets
- `id` (UUID) - Primary key
- `project_id` (UUID) - Foreign key to projects
- `name` (TEXT) - Dataset name
- `gcs_url` (TEXT) - GCP storage URL
- `size` (TEXT) - Dataset size
- `source` (TEXT) - Source (kaggle, etc.)
- `created_at` (TIMESTAMP)

### models
- `id` (UUID) - Primary key
- `project_id` (UUID) - Foreign key to projects
- `name` (TEXT) - Model name
- `framework` (TEXT) - Framework (pytorch)
- `gcs_url` (TEXT) - GCP storage URL
- `accuracy` (FLOAT) - Model accuracy
- `metadata` (JSONB) - Training metrics
- `created_at` (TIMESTAMP)

### agent_logs
- `id` (UUID) - Primary key
- `project_id` (UUID) - Foreign key to projects
- `agent_name` (TEXT) - Agent name
- `message` (TEXT) - Log message
- `log_level` (TEXT) - info/warning/error
- `created_at` (TIMESTAMP)

## Monitoring

### Check Database Status
```bash
python check-database-status.py
```

### Check Failed Projects
```bash
python check-failed-projects.py
```

### Fix Stuck Projects
```bash
python fix-stuck-projects.py
```

## Common Issues

### Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Windows - Find process using port
netstat -ano | findstr :8003

# Kill process
taskkill /PID <process_id> /F
```

### Agent Not Polling

**Problem**: Projects stuck in pending status

**Solution**:
1. Check if agent is running
2. Check health endpoint
3. Check polling status endpoint
4. Restart agent

### Database Connection Failed

**Problem**: `Connection refused` or `Authentication failed`

**Solution**:
1. Verify Supabase URL in `.env`
2. Verify Supabase key is service role key (not anon key)
3. Check internet connection
4. Check Supabase project is active

### GCP Upload Failed

**Problem**: `Failed to upload to GCP`

**Solution**:
1. Verify GCP credentials file exists
2. Verify bucket name is correct
3. Verify service account has Storage Admin role
4. Check bucket permissions

## Testing Workflow

### 1. Create Project

Frontend → ML Chat:
```
Create a flower classification model with dataset not more than 2GB
```

### 2. Monitor Progress

Watch project card in frontend:
- Status badge updates automatically (every 5s)
- Agent pipeline shows progress
- Click "View Details" to see logs

### 3. Check Logs

```bash
# In Supabase
SELECT * FROM agent_logs 
WHERE project_id = 'your-project-id' 
ORDER BY created_at DESC;
```

### 4. Download Model

When status is `completed`:
- Click "Download Model" button
- Get bundle with model + predict.py + labels

## Performance Tips

### For Faster Development
- Reduce epochs: `DEFAULT_EPOCHS=5`
- Reduce batch size: `BATCH_SIZE=32`
- Use smaller model: `preferred_model=mobilenet_v2`

### For Better Accuracy
- Increase epochs: `DEFAULT_EPOCHS=20`
- Increase batch size: `BATCH_SIZE=128` (if GPU available)
- Use larger model: `preferred_model=resnet50`

### For Production
- Enable mixed precision training (GPU only)
- Use larger batch sizes
- Enable model compilation (PyTorch 2.0+)
- Monitor GPU usage with `nvidia-smi`

## Architecture Diagram

```
┌─────────────┐
│   Frontend  │ :5173
│  (React)    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Backend   │ :4000
│  (Node.js)  │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ MCP Server  │ :8000
│  (Python)   │
└──────┬──────┘
       │
       ├──────→ Planner Agent :8001
       │        (Parse intent)
       │
       ├──────→ Dataset Agent :8002
       │        (Download data)
       │
       └──────→ Training Agent :8003
                (Train & Evaluate)
                
All agents ↔ Supabase (Database)
All agents ↔ GCP Storage (Files)
```

## Summary

✅ **All agents are configured and ready**
✅ **Auto-polling enabled** for Dataset and Training agents
✅ **Frontend auto-refresh** enabled (5s interval)
✅ **Windows compatible** with proper temp paths
✅ **GPU ready** (will use GPU if available)

Just start all services and create a project! 🚀
