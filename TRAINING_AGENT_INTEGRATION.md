# Training Agent Integration Summary

## Changes Made

### ✅ 1. Port Configuration
**File**: `Trainer-Agent/agent/main.py`
- Changed port from **8000** to **8003**
- Avoids conflict with MCP Server (port 8000)

### ✅ 2. Windows Compatibility
**Files Modified**:
- `Trainer-Agent/agent/services/training_service.py`
- `Trainer-Agent/agent/services/evaluation_service.py`

**Changes**:
- Replaced `/tmp/` paths with `tempfile.gettempdir()`
- Now works on Windows, Linux, and macOS

### ✅ 3. MCP Server Configuration
**File**: `mcp_server/.env`
- Added: `TRAINING_AGENT_URL=http://127.0.0.1:8003`

### ✅ 4. Startup Script
**File**: `start-training-agent.bat`
- Easy startup for Windows users

## Agent Capabilities

### Training Features
- ✅ **Auto-polling** for `pending_training` projects (every 10 seconds)
- ✅ **GPU support** (CUDA for NVIDIA, MPS for Apple Silicon, CPU fallback)
- ✅ **Pretrained models** (ResNet, MobileNet, EfficientNet)
- ✅ **Data augmentation** (flip, rotate, color jitter)
- ✅ **Smart dataset handling** (auto-split, validation creation)
- ✅ **Optimized training** (AdamW, learning rate scheduler)

### Evaluation Features
- ✅ **Auto-polling** for `pending_evaluation` projects
- ✅ **Comprehensive metrics** (accuracy, precision, recall, F1)
- ✅ **Per-class metrics** (classification report)
- ✅ **User bundle creation**:
  - `model.pth` - Trained model weights
  - `predict.py` - Ready-to-use inference script
  - `labels.json` - Class label mappings
  - `README.txt` - Usage instructions

## Architecture

```
User creates project
        ↓
Planner Agent (8001) → status: pending_dataset
        ↓
Dataset Agent (8002) → status: pending_training
        ↓
Training Agent (8003) → Trains model → status: pending_evaluation
        ↓
Training Agent (8003) → Evaluates model → status: completed
        ↓
User downloads bundle
```

## Status Flow

```
draft
  ↓
pending_dataset (Dataset Agent picks up)
  ↓
pending_training (Training Agent picks up)
  ↓
training (Training in progress)
  ↓
pending_evaluation (Training Agent picks up)
  ↓
evaluating (Evaluation in progress)
  ↓
completed (User can download bundle)
```

## Environment Setup

### Required Environment Variables

**File**: `Trainer-Agent/agent/.env`

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key

# GCP Configuration
GCP_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Logging
LOG_LEVEL=INFO

# Training Configuration (Optional)
BATCH_SIZE=64
DEFAULT_EPOCHS=10
DEFAULT_LEARNING_RATE=0.001
```

## Installation

### 1. Install Dependencies

```bash
cd Trainer-Agent/agent
pip install -r requirements.txt
```

### 2. Install PyTorch

**For CPU (Laptop without GPU)**:
```bash
pip install torch torchvision
```

**For NVIDIA GPU (Desktop with RTX)**:
```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 3. Configure Environment

Create `Trainer-Agent/agent/.env` with your credentials.

### 4. Start the Agent

**Windows**:
```bash
start-training-agent.bat
```

**Linux/Mac**:
```bash
cd Trainer-Agent/agent
python main.py
```

## Testing

### 1. Health Check

```bash
curl http://localhost:8003/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-10T..."
}
```

### 2. Polling Status

```bash
curl http://localhost:8003/agents/training/polling/status
```

Expected response:
```json
{
  "is_running": true,
  "poll_interval": 10,
  "processed_projects_count": 0
}
```

### 3. Manual Training Trigger (Optional)

```bash
curl -X POST http://localhost:8003/agents/training/start \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"your-project-id\"}"
```

## End-to-End Test

### 1. Start All Services

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

### 2. Create a Project

Open frontend at `http://localhost:5173` and create a project:
```
Create a flower classification model with dataset not more than 2GB
```

### 3. Watch the Pipeline

Monitor the project status in the frontend:
1. **pending_dataset** (yellow) - Dataset Agent working
2. **pending_training** (blue) - Training Agent working
3. **pending_evaluation** (blue) - Evaluation in progress
4. **completed** (green) - Ready to download!

### 4. Download the Bundle

Click "Download Model" button to get the trained model bundle.

## Monitoring

### Agent Logs

The Training Agent logs to:
- Console (stdout)
- Supabase `agent_logs` table

Watch for:
```
[2025-11-10 ...] Polling service started (interval: 10s)
[2025-11-10 ...] Found 1 project(s) pending training
[2025-11-10 ...] Triggering training for project: Flower Classification
✅ Using NVIDIA GPU (CUDA)  # or CPU
🚀 Starting training for 10 epochs on cuda
📊 Dataset: 5000 training images, 1000 validation images
📈 Epoch 1/10
✓ Epoch 1/10 - Train Loss: 0.8234 - Val Loss: 0.6543 - Val Acc: 78.50%
...
🎉 Training completed in 245.32s
[2025-11-10 ...] ✓ Training completed successfully
[2025-11-10 ...] Found 1 project(s) pending evaluation
[2025-11-10 ...] Triggering evaluation for project: Flower Classification
[2025-11-10 ...] ✓ Evaluation completed successfully
[2025-11-10 ...] Accuracy: 82.45%
```

### Database Monitoring

```bash
python check-database-status.py
```

Check for projects with status:
- `training` - Currently training
- `evaluating` - Currently evaluating
- `completed` - Ready for download

## Troubleshooting

### Agent Not Starting

**Problem**: Import errors or missing dependencies

**Solution**:
```bash
cd Trainer-Agent/agent
pip install -r requirements.txt
```

### Projects Stuck in pending_training

**Problem**: Training Agent not picking up projects

**Solution**:
1. Check if Training Agent is running: `curl http://localhost:8003/health`
2. Check polling status: `curl http://localhost:8003/agents/training/polling/status`
3. Check agent logs for errors
4. Verify database connection in `.env`

### Training Fails

**Problem**: Training crashes or fails

**Solution**:
1. Check agent logs in console
2. Check `agent_logs` table in Supabase
3. Common issues:
   - Dataset not found in GCP
   - Invalid dataset structure
   - Out of memory (reduce batch size)
   - Missing GCP credentials

### Evaluation Fails

**Problem**: Evaluation crashes after training

**Solution**:
1. Check if model was uploaded to GCP
2. Check if test dataset exists
3. Verify model architecture matches
4. Check agent logs for details

## Performance Notes

### CPU Training (Laptop)
- **Speed**: Slow (10-30 minutes per epoch)
- **Batch size**: 32 (default)
- **Recommended**: Use smaller models (MobileNet, ResNet18)
- **Epochs**: Reduce to 5-10 for faster testing

### GPU Training (Desktop with RTX)
- **Speed**: Fast (1-3 minutes per epoch)
- **Batch size**: 64-128 (depending on VRAM)
- **Recommended**: Any model works well
- **Epochs**: 10-20 for better accuracy

## Next Steps

### Immediate
1. ✅ Training Agent is ready to use
2. ✅ Start the agent with `start-training-agent.bat`
3. ✅ Test with a real project
4. ✅ Monitor logs and database

### Future Enhancements
- [ ] Add support for more model architectures
- [ ] Add hyperparameter tuning
- [ ] Add early stopping
- [ ] Add model quantization for mobile
- [ ] Add ONNX export for cross-platform inference
- [ ] Add TensorBoard logging
- [ ] Add distributed training support

## Summary

The Training Agent is now:
- ✅ **Configured** for port 8003
- ✅ **Windows compatible** with proper temp paths
- ✅ **Integrated** with MCP Server
- ✅ **Ready to use** with auto-polling
- ✅ **GPU ready** (will use GPU if available, CPU otherwise)

Just start it and it will automatically process projects! 🚀
