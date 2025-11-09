@echo off
echo ========================================
echo Starting Planner Agent on Port 8001
echo ========================================
echo.

cd Planner-Agent\agent\planner

echo Activating virtual environment...
call venv1\Scripts\activate

echo.
echo Starting Planner Agent...
echo.
echo The agent will be available at: http://127.0.0.1:8001
echo Health check: http://127.0.0.1:8001/health
echo.
echo Press Ctrl+C to stop the agent
echo.

uvicorn main:app --reload --port 8001
