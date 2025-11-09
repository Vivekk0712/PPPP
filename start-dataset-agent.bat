@echo off
echo ========================================
echo Starting Dataset Agent on Port 8002
echo ========================================
echo.

cd Dataset_Agent\agents\dataset

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting Dataset Agent...
echo.
echo The agent will be available at: http://127.0.0.1:8002
echo Health check: http://127.0.0.1:8002/health
echo.
echo Auto-polling is ENABLED - will automatically process pending_dataset projects
echo.
echo Press Ctrl+C to stop the agent
echo.

python main.py
