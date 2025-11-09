# 🧪 Complete Testing Guide - Planner Agent Integration

## ✅ Pre-Flight Checklist

Before testing, ensure all these are ready:

### 1. Package Versions Fixed
```bash
cd Planner-Agent/agent/planner
pip uninstall -y supabase httpx gotrue
pip install -r requirements.txt
```

### 2. Environment Variables Set

**Planner Agent (.env):**
```env
✅ SUPABASE_URL
✅ SUPABASE_KEY
✅ GEMINI_API_KEY
✅ LOG_LEVEL=INFO
```

**MCP Server (.env):**
```env
✅ SUPABASE_URL
✅ SUPABASE_SERVICE_ROLE_KEY
✅ GEMINI_API_KEY
✅ PLANNER_AGENT_URL=http://127.0.0.1:8001
```

**Backend (.env):**
```env
✅ PORT=4000
✅ MCP_SERVER_URL=http://127.0.0.1:8000
✅ FIREBASE_PROJECT_ID
✅ GOOGLE_APPLICATION_CREDENTIALS
```

### 3. Database Tables Created

Run this SQL in Supabase:

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'messages', 'projects', 'datasets', 'models', 'agent_logs');

-- If any are missing, create them from SETUP_GUIDE.md
```

---

## 🚀 Startup Sequence

### Terminal 1: Planner Agent (Port 8001)
```bash
cd Planner-Agent/agent/planner
venv1\Scripts\activate
uvicorn main:app --reload --port 8001
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\Dell\\...\\planner']
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using WatchFilesProcess
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Test:** Open http://127.0.0.1:8001/health
```json
{
  "status": "healthy",
  "agent": "planner",
  "timestamp": "2025-01-09T..."
}
```

---

### Terminal 2: MCP Server (Port 8000)
```bash
cd mcp_server
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\Dell\\...\\mcp_server']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using StatReloadProcess
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Test:** Open http://127.0.0.1:8000/health
```json
{
  "status": "ok"
}
```

---

### Terminal 3: Backend (Port 4000)
```bash
cd backend
npm start
```

**Expected Output:**
```
> backend@1.0.0 start
> node src/index.js

✅ Server running on port 4000
```

✅ **Test:** Open http://localhost:4000/api/me (should return 401 if not logged in)

---

### Terminal 4: Frontend (Port 5173)
```bash
cd frontend
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

✅ **Test:** Open http://localhost:5173 (should see login page)

---

## 🧪 Integration Tests

### Test 1: Health Checks ✅

**Check all services are running:**

```bash
# Planner Agent
curl http://127.0.0.1:8001/health

# MCP Server
curl http://127.0.0.1:8000/health

# Backend (will return 401 - that's OK)
curl http://localhost:4000/api/me
```

**Expected:** All return responses (not connection errors)

---

### Test 2: Direct Planner Agent Call ✅

**Test the Planner Agent directly:**

```bash
curl -X POST http://127.0.0.1:8001/agents/planner/handle_message \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"test-user-123\",\"session_id\":\"test-session-123\",\"message_text\":\"Train a model to classify cat and dog images\"}"
```

**Expected Response:**
```json
{
  "success": true,
  "project_id": "uuid-here",
  "message": "Project plan created successfully",
  "plan": {
    "name": "Cat and Dog Image Classifier",
    "task_type": "image_classification",
    "framework": "pytorch",
    "dataset_source": "kaggle",
    "search_keywords": ["cat", "dog", "classification", "pets"],
    "preferred_model": "resnet18",
    "target_metric": "accuracy",
    "target_value": 0.9,
    "max_dataset_size_gb": 50
  }
}
```

**Check Supabase:**
```sql
SELECT * FROM projects WHERE user_id = 'test-user-123' ORDER BY created_at DESC LIMIT 1;
SELECT * FROM agent_logs WHERE agent_name = 'planner' ORDER BY created_at DESC LIMIT 5;
```

---

### Test 3: MCP to Planner Agent ✅

**Test MCP calling Planner Agent:**

```bash
curl -X POST http://127.0.0.1:8000/api/ml/planner \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"test-user-456\",\"message\":\"Create a flower classification model\"}"
```

**Expected Response:**
```json
{
  "reply": "Project plan created successfully",
  "projectId": "uuid-here",
  "status": "pending_dataset",
  "plan": {
    "name": "Flower Classification Model",
    ...
  }
}
```

---

### Test 4: Full Stack Test (Frontend → Backend → MCP → Planner) ✅

**Steps:**

1. **Open Frontend:** http://localhost:5173
2. **Login:** Use Google, Email, or Phone
3. **Navigate:** Click "ML Projects" tab
4. **Type Message:** In the ML Chat, type:
   ```
   Train a model to classify plant diseases
   ```
5. **Send:** Click the send button (📤)
6. **Wait:** Watch for response (should take 2-5 seconds)

**Expected Results:**

✅ **In Chat:**
- User message appears
- Loading spinner shows
- Assistant response appears with project details

✅ **In Project List:**
- New project card appears
- Status badge: "Pending Dataset" (blue)
- Progress bar: 25%
- Keywords displayed
- "View Details" button visible

✅ **In Project Details Modal:**
- Click "View Details"
- Agent Pipeline shows:
  - ✅ Planner (green, completed)
  - ⚪ Dataset (gray, pending)
  - ⚪ Training (gray, pending)
  - ⚪ Evaluation (gray, pending)
- Details tab shows project info
- Agent Logs tab shows planner logs
- Metadata tab shows JSON

✅ **In Supabase:**
```sql
-- Check project created
SELECT * FROM projects ORDER BY created_at DESC LIMIT 1;

-- Check agent logs
SELECT * FROM agent_logs WHERE agent_name = 'planner' ORDER BY created_at DESC LIMIT 5;

-- Check messages
SELECT * FROM messages WHERE role = 'assistant' ORDER BY created_at DESC LIMIT 1;
```

---

## 🎯 Test Scenarios

### Scenario 1: Simple Classification
**Input:** "Train a model to classify cats and dogs"

**Expected:**
- Project Name: "Cat and Dog Classifier" (or similar)
- Keywords: ["cat", "dog", "classification"]
- Model: resnet18
- Status: pending_dataset

---

### Scenario 2: Medical Imaging
**Input:** "Create an image classifier for skin cancer detection"

**Expected:**
- Project Name: "Skin Cancer Detection Classifier" (or similar)
- Keywords: ["skin cancer", "medical imaging", "dermatology"]
- Model: resnet50 or efficientnet (more complex)
- Status: pending_dataset

---

### Scenario 3: Plant Disease
**Input:** "Build a model to identify tomato leaf diseases"

**Expected:**
- Project Name: "Tomato Leaf Disease Identifier" (or similar)
- Keywords: ["tomato", "leaf disease", "plant pathology"]
- Model: resnet18
- Status: pending_dataset

---

### Scenario 4: Vague Request
**Input:** "I want to do machine learning"

**Expected:**
- Planner may ask for clarification
- Or create a generic project
- Check agent logs for any errors

---

## 🐛 Troubleshooting

### Issue: Planner Agent won't start

**Error:** `TypeError: Client.__init__() got an unexpected keyword argument 'proxy'`

**Fix:**
```bash
cd Planner-Agent/agent/planner
pip uninstall -y supabase httpx gotrue
pip install supabase==2.9.0 httpx==0.27.0
```

---

### Issue: MCP Server won't start

**Error:** `ValidationError: planner_agent_url Extra inputs are not permitted`

**Fix:** Already fixed! The Settings class now includes PLANNER_AGENT_URL

---

### Issue: "Planner Agent service unavailable"

**Cause:** Planner Agent not running

**Fix:**
1. Check Terminal 1 - is Planner Agent running?
2. Test: `curl http://127.0.0.1:8001/health`
3. If not responding, restart Planner Agent

---

### Issue: "Gemini API error"

**Cause:** Invalid or missing API key

**Fix:**
1. Check `.env` files have valid GEMINI_API_KEY
2. Get new key: https://makersuite.google.com/app/apikey
3. Update both:
   - `Planner-Agent/agent/planner/.env`
   - `mcp_server/.env`
4. Restart both services

---

### Issue: Projects not appearing in UI

**Cause:** Frontend not refreshing

**Fix:**
1. Switch to another tab and back
2. Or refresh the page (F5)
3. Check browser console for errors

---

### Issue: "Database error"

**Cause:** Missing tables or wrong credentials

**Fix:**
1. Check Supabase URL and keys are correct
2. Verify tables exist:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```
3. Create missing tables from SETUP_GUIDE.md

---

## 📊 Success Metrics

### ✅ All Tests Pass When:

1. **Health Checks:** All 3 services respond
2. **Direct Call:** Planner Agent creates project
3. **MCP Call:** MCP successfully calls Planner
4. **Full Stack:** Frontend → Backend → MCP → Planner works
5. **Database:** Projects and logs appear in Supabase
6. **UI:** Projects display correctly with status and progress
7. **Logs:** Agent logs visible in UI

---

## 🎉 Final Verification

Run this complete test:

1. ✅ Start all 4 services
2. ✅ Check all health endpoints
3. ✅ Login to frontend
4. ✅ Create 3 different projects with different prompts
5. ✅ Verify all 3 appear in project list
6. ✅ Click "View Details" on each
7. ✅ Check Agent Logs tab
8. ✅ Verify in Supabase database

**If all pass:** 🎊 **INTEGRATION SUCCESSFUL!** 🎊

---

## 📝 Test Results Template

```
Date: ___________
Tester: ___________

[ ] Planner Agent starts successfully
[ ] MCP Server starts successfully
[ ] Backend starts successfully
[ ] Frontend starts successfully
[ ] Health checks pass
[ ] Direct Planner call works
[ ] MCP to Planner call works
[ ] Full stack test works
[ ] Projects appear in UI
[ ] Agent logs visible
[ ] Database entries correct

Issues Found:
_________________________________
_________________________________

Notes:
_________________________________
_________________________________
```

---

## 🚀 Next Steps After Testing

Once all tests pass:

1. ✅ Planner Agent is working
2. ⏳ Integrate Dataset Agent
3. ⏳ Integrate Training Agent
4. ⏳ Integrate Evaluation Agent
5. ⏳ Add real-time updates
6. ⏳ Deploy to production

---

## 📚 Related Documentation

- `PLANNER_AGENT_INTEGRATION.md` - Integration details
- `INTEGRATION_COMPLETE.md` - Success summary
- `SETUP_GUIDE.md` - Initial setup
- `FEATURE_STATUS.md` - Feature status
- `QUICK_START.md` - Quick start guide

---

**Happy Testing! 🧪✨**
