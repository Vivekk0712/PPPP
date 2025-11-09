# Planner Agent Integration Guide

## 🎯 Overview

The Planner Agent is now fully integrated with the AutoML platform! It uses Gemini AI to parse user messages and create structured ML project plans.

## 🏗️ Architecture

```
User (Frontend)
    ↓
Backend (Node.js) - Port 4000
    ↓
MCP Server (Python) - Port 8000
    ↓
Planner Agent (Python) - Port 8001
    ↓
Supabase Database
```

## 📋 What the Planner Agent Does

1. **Receives** user message from ML Chat
2. **Parses** intent using Gemini AI
3. **Extracts**:
   - Project name
   - Task type (image classification)
   - Search keywords for datasets
   - Preferred model architecture
   - Target accuracy
4. **Creates** project in Supabase with status `pending_dataset`
5. **Logs** activity to `agent_logs` table
6. **Sends** confirmation message back to user

## 🚀 How to Start

### Step 1: Fix Supabase Package Issue

In the Planner Agent directory, run:

```bash
cd Planner-Agent/agent/planner
pip uninstall -y supabase httpx gotrue
pip install -r requirements.txt
```

### Step 2: Start the Planner Agent

**Windows:**
```bash
cd Planner-Agent/agent/planner
venv1\Scripts\activate
uvicorn main:app --reload --port 8001
```

**Linux/Mac:**
```bash
cd Planner-Agent/agent/planner
source venv1/bin/activate
uvicorn main:app --reload --port 8001
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

### Step 3: Start MCP Server

In a new terminal:

```bash
cd mcp_server
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

uvicorn main:app --reload --port 8000
```

### Step 4: Start Backend

In another terminal:

```bash
cd backend
npm start
```

### Step 5: Start Frontend

In another terminal:

```bash
cd frontend
npm run dev
```

## 🧪 Testing the Integration

### 1. Open the Frontend
Navigate to http://localhost:5173

### 2. Login
Sign in with Google, Email, or Phone

### 3. Go to ML Projects Tab
Click on "ML Projects" in the navigation

### 4. Use the ML Chat
Try these example messages:

**Example 1:**
```
Train a model to classify plant diseases
```

**Example 2:**
```
Create an image classifier for skin cancer detection
```

**Example 3:**
```
Build a model to identify different types of flowers
```

### 5. Watch the Magic! ✨

The Planner Agent will:
1. Parse your message with Gemini
2. Create a project plan
3. Insert it into Supabase
4. Show it in the project list
5. Display status as "Pending Dataset"

## 📊 What You'll See

### In the Frontend:
- ✅ Project card appears in the list
- ✅ Status badge shows "Pending Dataset"
- ✅ Progress bar at 25%
- ✅ Project name extracted from your message
- ✅ Keywords displayed

### In the Database (Supabase):
- ✅ New row in `projects` table
- ✅ New rows in `agent_logs` table
- ✅ New row in `messages` table (confirmation)

### In the Logs:
**Planner Agent Terminal:**
```
INFO: Received message from user abc123
INFO: Project created successfully: Plant Disease Classifier
```

**MCP Server Terminal:**
```
INFO: ML Planner request from user abc123
INFO: Planner Agent created project xyz789
```

## 🔍 Checking if It Works

### Method 1: Check Planner Agent Health
```bash
curl http://127.0.0.1:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "agent": "planner",
  "timestamp": "2025-01-09T..."
}
```

### Method 2: Test Direct API Call
```bash
curl -X POST http://127.0.0.1:8001/agents/planner/handle_message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "session_id": "test-session",
    "message_text": "Train a model for cat vs dog classification"
  }'
```

### Method 3: Check Supabase
1. Go to your Supabase dashboard
2. Open SQL Editor
3. Run:
```sql
SELECT * FROM projects ORDER BY created_at DESC LIMIT 5;
SELECT * FROM agent_logs ORDER BY created_at DESC LIMIT 10;
```

## 🐛 Troubleshooting

### Issue 1: "Planner Agent service unavailable"

**Cause:** Planner Agent not running

**Fix:**
```bash
cd Planner-Agent/agent/planner
uvicorn main:app --reload --port 8001
```

### Issue 2: "TypeError: Client.__init__() got an unexpected keyword argument 'proxy'"

**Cause:** Incompatible supabase/httpx versions

**Fix:**
```bash
pip uninstall -y supabase httpx gotrue
pip install supabase==2.9.0 httpx==0.27.0
```

### Issue 3: "Gemini API error"

**Cause:** Invalid or missing GEMINI_API_KEY

**Fix:**
1. Check `.env` file has valid key
2. Get new key from https://makersuite.google.com/app/apikey
3. Update both:
   - `Planner-Agent/agent/planner/.env`
   - `mcp_server/.env`

### Issue 4: Projects not appearing in UI

**Cause:** Frontend not refreshing

**Fix:**
1. Click away from ML Projects tab
2. Click back to ML Projects tab
3. Or refresh the page

### Issue 5: "Database error"

**Cause:** Supabase tables not created

**Fix:**
Run the SQL from `SETUP_GUIDE.md` to create tables:
```sql
create table if not exists projects (...);
create table if not exists agent_logs (...);
```

## 📝 Environment Variables

### Planner Agent (.env)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
GEMINI_API_KEY=your-gemini-key
LOG_LEVEL=INFO
```

### MCP Server (.env)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
GEMINI_API_KEY=your-gemini-key
PLANNER_AGENT_URL=http://127.0.0.1:8001
```

### Backend (.env)
```env
MCP_SERVER_URL=http://127.0.0.1:8000
```

## 🎯 Expected Flow

1. **User types** in ML Chat: "Train a plant disease classifier"
2. **Frontend** sends to Backend: `POST /api/ml/chat`
3. **Backend** forwards to MCP: `POST /api/ml/planner`
4. **MCP** calls Planner Agent: `POST /agents/planner/handle_message`
5. **Planner Agent**:
   - Calls Gemini AI
   - Parses response
   - Creates project in Supabase
   - Logs to agent_logs
   - Returns success
6. **MCP** returns to Backend
7. **Backend** returns to Frontend
8. **Frontend** refreshes project list
9. **User sees** new project card!

## 🔄 Next Steps

After the Planner Agent creates a project:

1. **Status**: `pending_dataset`
2. **Next Agent**: Dataset Agent (to be integrated)
3. **Action**: Download dataset from Kaggle
4. **Then**: Training Agent → Evaluation Agent

## 📚 Files Modified

### New Files:
- `PLANNER_AGENT_INTEGRATION.md` (this file)

### Modified Files:
- `mcp_server/main.py` - Updated `/api/ml/planner` endpoint
- `mcp_server/.env` - Added `PLANNER_AGENT_URL`
- `Planner-Agent/agent/planner/requirements.txt` - Fixed versions

### Existing Files (No Changes Needed):
- `frontend/src/components/MLChatBot.jsx` ✅
- `frontend/src/services/mlApi.js` ✅
- `backend/src/routes/ml.js` ✅

## ✅ Success Criteria

You'll know it's working when:

1. ✅ Planner Agent starts without errors
2. ✅ MCP Server connects to Planner Agent
3. ✅ User message creates project in Supabase
4. ✅ Project appears in frontend UI
5. ✅ Agent logs show in database
6. ✅ Status shows "Pending Dataset"
7. ✅ Progress bar shows 25%

## 🎉 You're Done!

The Planner Agent is now fully integrated! Users can create ML projects by simply chatting with the ML Assistant. The agent will intelligently parse their requests and create structured project plans.

**Next:** Integrate the Dataset Agent to automatically fetch datasets from Kaggle!
