# 🚀 Quick Reference Card

## Start All Services (Copy & Paste)

### Windows PowerShell

**Terminal 1 - Planner Agent:**
```powershell
cd Planner-Agent\agent\planner
.\venv1\Scripts\Activate.ps1
uvicorn main:app --reload --port 8001
```

**Terminal 2 - Dataset Agent:**
```powershell
cd Dataset_Agent\agents\dataset
.\venv\Scripts\Activate.ps1
python main.py
```

**Terminal 3 - MCP Server:**
```powershell
cd mcp_server
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

**Terminal 4 - Backend:**
```powershell
cd backend
npm start
```

**Terminal 5 - Frontend:**
```powershell
cd frontend
npm run dev
```

---

## Quick Health Checks

```bash
# Planner Agent
curl http://127.0.0.1:8001/health

# MCP Server
curl http://127.0.0.1:8000/health

# Frontend
# Open: http://localhost:5173
```

---

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| Planner Agent | 8001 | http://127.0.0.1:8001 |
| Dataset Agent | 8002 | http://127.0.0.1:8002 |
| MCP Server | 8000 | http://127.0.0.1:8000 |
| Backend | 4000 | http://localhost:4000 |
| Frontend | 5173 | http://localhost:5173 |

---

## Common Commands

### Fix Planner Agent Package Issue
```bash
cd Planner-Agent/agent/planner
pip uninstall -y supabase httpx gotrue
pip install -r requirements.txt
```

### Check Database
```sql
-- Recent projects
SELECT * FROM projects ORDER BY created_at DESC LIMIT 5;

-- Recent logs
SELECT * FROM agent_logs ORDER BY created_at DESC LIMIT 10;
```

### Test Planner Agent Directly
```bash
curl -X POST http://127.0.0.1:8001/agents/planner/handle_message \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"test\",\"session_id\":\"test\",\"message_text\":\"Train a cat classifier\"}"
```

---

## Test Messages

Try these in the ML Chat:

1. "Train a model to classify plant diseases"
2. "Create an image classifier for skin cancer detection"
3. "Build a model to identify different types of flowers"
4. "Train a cat vs dog classifier"

---

## Troubleshooting Quick Fixes

| Error | Fix |
|-------|-----|
| Planner Agent won't start | `pip install supabase==2.9.0 httpx==0.27.0` |
| MCP Server validation error | Already fixed in code |
| Service unavailable | Check if Planner Agent is running |
| Gemini API error | Check GEMINI_API_KEY in .env files |
| Projects not showing | Refresh page or switch tabs |

---

## File Locations

```
Auth_System_MCP-main/
├── Planner-Agent/agent/planner/
│   ├── main.py              # Planner service
│   ├── .env                 # Planner config
│   └── requirements.txt     # Planner packages
│
├── mcp_server/
│   ├── main.py              # MCP orchestrator
│   └── .env                 # MCP config
│
├── backend/
│   ├── src/routes/ml.js     # ML routes
│   └── .env                 # Backend config
│
└── frontend/
    ├── src/components/
    │   └── MLChatBot.jsx    # ML chat interface
    └── .env                 # Frontend config
```

---

## Environment Variables Checklist

### Planner Agent (.env)
- [ ] SUPABASE_URL
- [ ] SUPABASE_KEY
- [ ] GEMINI_API_KEY
- [ ] LOG_LEVEL

### MCP Server (.env)
- [ ] SUPABASE_URL
- [ ] SUPABASE_SERVICE_ROLE_KEY
- [ ] GEMINI_API_KEY
- [ ] PLANNER_AGENT_URL

### Backend (.env)
- [ ] PORT
- [ ] MCP_SERVER_URL
- [ ] FIREBASE_PROJECT_ID
- [ ] GOOGLE_APPLICATION_CREDENTIALS

---

## Success Indicators

✅ **Working When:**
- All 4 services start without errors
- Health checks return 200 OK
- Can create projects via ML Chat
- Projects appear in UI
- Agent logs visible in database
- Status shows "Pending Dataset"
- Progress bar at 25%

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| `TESTING_GUIDE.md` | Complete testing instructions |
| `PLANNER_AGENT_INTEGRATION.md` | Integration details |
| `INTEGRATION_COMPLETE.md` | Success summary |
| `SETUP_GUIDE.md` | Initial setup |
| `FEATURE_STATUS.md` | Feature completion status |
| `QUICK_START.md` | Quick start guide |
| `QUICK_REFERENCE.md` | This file |

---

**Need Help?** Check `TESTING_GUIDE.md` for detailed troubleshooting!
