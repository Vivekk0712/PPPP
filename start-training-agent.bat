@echo off
echo ============================================================
echo Starting Training Agent (Port 8003)
echo ============================================================
echo.
echo This agent handles:
echo   - Model Training (PyTorch)
echo   - Model Evaluation
echo   - Bundle Creation
echo.
echo Auto-polling enabled for:
echo   - pending_training projects
echo   - pending_evaluation projects
echo.
echo ============================================================
echo.

cd Trainer-Agent\agent
python main.py
