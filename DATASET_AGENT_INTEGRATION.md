# 📦 Dataset Agent Integration Guide

## 🎯 Overview

The Dataset Agent is now integrated with the AutoML platform! It automatically:
1. Watches for projects with status `pending_dataset`
2. Searches Kaggle for relevant datasets
3. Downloads the best matching dataset
4. Uploads to Google Cloud Storage
5. Updates project status to `pending_training`

## 🏗️ Architecture

```
Planner Agent (Port 8001)
    ↓ Creates project with status "pending_dataset"
MCP Server (Port 8000)
    ↓ Automatically triggers
Dataset Agent (Port 8002)
    ↓ Searches Kaggle
    ↓ Downloads dataset
    ↓ Uploads to GCP
    ↓ Updates status to "pending_training"
Supabase Database
```

## 🚀 How to Start

### Step 1: Start Dataset Agent

**Windows:**
```bash
cd Dataset_Agent/agents/dataset
venv\Scripts\activate
uvicorn main:app --reload --port 8002
```

**Linux/Mac:**
```bash
cd Dataset_Agent/agents/dataset
source venv/bin/activate
uvicorn main:app --reload --port 8002
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX]
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Verify Dataset Agent is Running

```bash
curl http://127.0.0.1:8002/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "agent": "dataset",
  "timestamp": "2025-01-09T..."
}
```

### Step 3: Start All Other Services

```bash
# Terminal 1 - Planner Agent (Port 8001)
cd Planner-Agent/agent/planner
venv1\Scripts\activate
uvicorn main:app --reload --port 8001

# Terminal 2 - Dataset Agent (Port 8002) - Already started above
# Terminal 3 - MCP Server (Port 8000)
cd mcp_server
venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Terminal 4 - Backend (Port 4000)
cd backend
npm start

# Terminal 5 - Frontend (Port 5173)
cd frontend
npm run dev
```

## 🔄 Automatic Workflow

### What Happens Automatically:

1. **User creates project** via ML Chat
   ```
   "Train a model to classify plant diseases"
   ```

2. **Planner Agent** creates project
   - Status: `pending_dataset`
   - Keywords: ["plant", "disease", "classification"]

3. **MCP Server** automatically triggers Dataset Agent
   - Sends project_id to Dataset Agent
   - Dataset Agent starts processing

4. **Dataset Agent** processes:
   - Searches Kaggle with keywords
   - Ranks datasets by relevance
   - Downloads best match
   - Uploads to GCP bucket
   - Updates status to `pending_training`

5. **User sees** progress in UI
   - Status changes from "Pending Dataset" to "Pending Training"
   - Progress bar moves from 25% to 50%
   - Agent logs show dataset download activity

## 📊 Status Flow

```
draft
  ↓ (Planner Agent)
pending_dataset ← You are here
  ↓ (Dataset Agent)
pending_training
  ↓ (Training Agent)
pending_evaluation
  ↓ (Evaluation Agent)
completed
```

## 🧪 Testing

### Test 1: Health Check
```bash
curl http://127.0.0.1:8002/health
```

### Test 2: Manual Trigger
```bash
curl -X POST http://127.0.0.1:8002/agents/dataset/start \
  -H "Content-Type: application/json" \
  -d '{"project_id":"your-project-id-here"}'
```

### Test 3: Full Workflow
1. Open frontend: http://localhost:5173
2. Login
3. Go to ML Projects tab
4. Create project: "Train a plant disease classifier"
5. Watch the status change automatically!

## 📝 Configuration

### Dataset Agent (.env)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
GCP_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-key
```

### MCP Server (.env)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
GEMINI_API_KEY=your-gemini-key
PLANNER_AGENT_URL=http://127.0.0.1:8001
DATASET_AGENT_URL=http://127.0.0.1:8002
```

## 🔍 Monitoring

### Check Agent Logs in UI
1. Go to ML Projects
2. Click "View Details" on a project
3. Click "Agent Logs" tab
4. See Dataset Agent activity:
   - "Searching Kaggle for datasets..."
   - "Found X datasets matching keywords"
   - "Downloading dataset: dataset-name"
   - "Uploading to GCP..."
   - "Dataset uploaded successfully"

### Check Database
```sql
-- Check project status
SELECT id, name, status, updated_at 
FROM projects 
ORDER BY updated_at DESC 
LIMIT 5;

-- Check agent logs
SELECT agent_name, message, log_level, created_at
FROM agent_logs
WHERE agent_name = 'dataset'
ORDER BY created_at DESC
LIMIT 10;

-- Check datasets table
SELECT project_id, name, gcs_url, size
FROM datasets
ORDER BY created_at DESC
LIMIT 5;
```

## 🐛 Troubleshooting

### Issue: Dataset Agent won't start

**Error:** Package compatibility issues

**Fix:**
```bash
cd Dataset_Agent/agents/dataset
pip install -r requirements.txt
```

### Issue: "Kaggle API error"

**Cause:** Missing or invalid Kaggle credentials

**Fix:**
1. Get Kaggle API key from https://www.kaggle.com/settings/account
2. Update `.env` file:
   ```env
   KAGGLE_USERNAME=your-username
   KAGGLE_KEY=your-api-key
   ```
3. Restart Dataset Agent

### Issue: "GCP upload failed"

**Cause:** Missing or invalid GCP credentials

**Fix:**
1. Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
2. Verify service account has Storage Admin role
3. Check bucket name is correct
4. Restart Dataset Agent

### Issue: Status not updating

**Cause:** Dataset Agent not triggered or failed

**Fix:**
1. Check Dataset Agent logs in terminal
2. Check agent_logs table in Supabase
3. Manually trigger: 
   ```bash
   curl -X POST http://127.0.0.1:8002/agents/dataset/start \
     -H "Content-Type: application/json" \
     -d '{"project_id":"project-id"}'
   ```

## 📊 Success Indicators

✅ **Working When:**
- Dataset Agent starts without errors
- Health check returns 200 OK
- Project status changes from `pending_dataset` to `pending_training`
- Dataset entry appears in `datasets` table
- Agent logs show successful download and upload
- GCS bucket contains the dataset file
- UI shows progress bar at 50%

## 🎯 What's Next

After Dataset Agent completes:
1. ⏳ **Training Agent** will pick up the project
2. ⏳ Downloads dataset from GCP
3. ⏳ Trains PyTorch model
4. ⏳ Uploads model to GCP
5. ⏳ Updates status to `pending_evaluation`

## 📚 Related Documentation

- `PLANNER_AGENT_INTEGRATION.md` - Planner Agent setup
- `TESTING_GUIDE.md` - Complete testing instructions
- `FEATURE_STATUS.md` - Feature completion status
- `QUICK_REFERENCE.md` - Quick commands

## 🎉 Success!

The Dataset Agent is now integrated! Your AutoML platform can now:
1. ✅ Parse user intent (Planner Agent)
2. ✅ Find and download datasets (Dataset Agent)
3. ⏳ Train models (Training Agent - next)
4. ⏳ Evaluate models (Evaluation Agent - next)

**Progress: 92% Complete!** 🚀
