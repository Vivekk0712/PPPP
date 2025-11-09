---
inclusion: always
---

# AutoML Platform - Project Overview

## Architecture

This is a multi-agent AutoML platform with the following components:

### Frontend (React + Vite)
- Port: 5173
- Location: `frontend/`
- Beautiful UI with ML project management, chat interface, and model testing

### Backend (Node.js + Express)
- Port: 4000
- Location: `backend/`
- Handles authentication, session management, and API routing

### MCP Server (Python + FastAPI)
- Port: 8000
- Location: `mcp_server/`
- Orchestrates all AI agents and manages communication

### AI Agents

#### Planner Agent (Port 8001)
- Location: `Planner-Agent/agent/planner/`
- Uses Gemini AI to parse user intent
- Creates structured ML project plans
- Extracts dataset size limits from user messages

#### Dataset Agent (Port 8002)
- Location: `Dataset_Agent/agents/dataset/`
- Auto-polls for projects with status `pending_dataset`
- Searches Kaggle for datasets
- Downloads and uploads to GCP
- Updates status to `pending_training`

#### Training Agent (Port 8003) - To be integrated
- Will train PyTorch models
- Downloads datasets from GCP
- Uploads trained models

#### Evaluation Agent (Port 8004) - To be integrated
- Will evaluate trained models
- Creates downloadable model bundles

## Database (Supabase)

Tables:
- `users` - User profiles (Firebase UID → UUID mapping)
- `messages` - Chat history
- `projects` - ML project metadata
- `datasets` - Dataset information
- `models` - Trained model information
- `agent_logs` - Agent execution logs

## Key Features

1. **Firebase UID → User UUID Conversion**: All endpoints convert Firebase UID to database UUID
2. **Dataset Size Limits**: Users can specify size limits in prompts (e.g., "not more than 1GB")
3. **Auto-Polling**: Dataset Agent automatically processes pending projects every 10 seconds
4. **Agent Logs**: All agent activities are logged and visible in UI
5. **Real-time Status**: Projects show progress through pipeline (25%, 50%, 75%, 100%)

## Important Notes

- Always convert Firebase UID to User UUID before database queries
- Dataset Agent uses auto-polling, no manual triggering needed
- Gemini AI extracts size limits and converts MB to GB automatically
- All datetime fields use UTC timestamps
