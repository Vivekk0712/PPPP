@echo off
echo ========================================
echo Starting All AutoML Agents
echo ========================================
echo.
echo This will open 5 terminal windows:
echo 1. Planner Agent (Port 8001)
echo 2. Dataset Agent (Port 8002)
echo 3. MCP Server (Port 8000)
echo 4. Backend (Port 4000)
echo 5. Frontend (Port 5173)
echo.
pause

start "Planner Agent" cmd /k "cd Planner-Agent\agent\planner && venv1\Scripts\activate && uvicorn main:app --reload --port 8001"

timeout /t 2

start "Dataset Agent" cmd /k "cd Dataset_Agent\agents\dataset && venv\Scripts\activate && uvicorn main:app --reload --port 8002"

timeout /t 2

start "MCP Server" cmd /k "cd mcp_server && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

timeout /t 2

start "Backend" cmd /k "cd backend && npm start"

timeout /t 2

start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo All services are starting...
echo ========================================
echo.
echo Check each terminal window for status
echo Frontend will be available at: http://localhost:5173
echo.
pause
