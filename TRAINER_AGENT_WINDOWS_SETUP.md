# Trainer Agent - Setup & Download Feature

## Quick Summary

The Trainer Agent is a **combined Training + Evaluation agent** that:
- ✅ Already supports NVIDIA GPU (CUDA)
- ✅ Has auto-polling for both `pending_training` and `pending_evaluation`
- ✅ Handles complete workflow: Train → Evaluate → Create Bundle
- ✅ Download feature implemented (MCP Server + Frontend)
- ⚠️ Needs port change (8000 → 8003)
- ⚠️ Needs Windows temp directory fix
- ⚠️ Needs PyTorch CUDA installation

## Download Feature

### How It Works

1. **Training Agent** creates a bundle after evaluation:
   - `model.pth` - Trained weights
   - `predict.py` - Inference script
   - `labels.json` - Class mappings
   - `README.txt` - Usage guide

2. **Bundle uploaded to GCP** and URL stored in project metadata

3. **Frontend shows download button** for completed projects

4. **MCP Server streams file** from GCP to user

### Implementation

**MCP Server** (`mcp_server/main.py`):
- ✅ Implemented `/api/ml/projects/{project_id}/download` endpoint
- ✅ Fetches bundle URL from project metadata
- ✅ Downloads from GCP and streams to client

**Frontend** (`frontend/src/pages/MLProjectsPage.jsx`):
- ✅ Shows download button on completed projects
- ✅ Shows bundle contents in project details modal
- ✅ Downloads as ZIP file with project name

**Backend** (`backend/src/routes/ml.js`):
- ✅ Already proxies download requests to MCP Server

## Required Changes

### 1. Fix Port Conflict

**File**: `Trainer-Agent/agent/main.py` (line ~280)

```python
# Change from:
port=8000,

# To:
port=8003,
```

### 2. Fix Windows Temp Directory Paths

#### File 1: `Trainer-Agent/agent/services/training_service.py`

**Line ~90**:
```python
# OLD
temp_dir = f"/tmp/training_{project_id}"

# NEW
import tempfile
temp_dir = os.path.join(tempfile.gettempdir(), f"training_{project_id}")
```

**Line ~140**:
```python
# OLD
dataset_extract_dir = os.path.join(temp_dir, "dataset")

# Already correct, no change needed
```

#### File 2: `Trainer-Agent/agent/services/evaluation_service.py`

**Line ~80**:
```python
# OLD
temp_dir = f"/tmp/evaluation_{project_id}"

# NEW
import tempfile
temp_dir = os.path.join(tempfile.gettempdir(), f"evaluation_{project_id}")
```

**Line ~350** (in `create_user_bundle` function):
```python
# OLD
export_dir = f"/tmp/export_{project_id}"
zip_path = f"/tmp/{zip_filename}"

# NEW
import tempfile
export_dir = os.path.join(tempfile.gettempdir(), f"export_{project_id}")
zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
```

### 3. Create .env File

**File**: `Trainer-Agent/agent/.env`

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key

# GCP Configuration
GCP_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=C:/path/to/service-account-key.json

# Logging
LOG_LEVEL=INFO

# Training Configuration (Optional - these are defaults)
BATCH_SIZE=64
DEFAULT_EPOCHS=10
DEFAULT_LEARNING_RATE=0.001
```

### 4. Install PyTorch with CUDA

```bash
cd Trainer-Agent/agent

# Uninstall CPU version
pip uninstall torch torchvision

# Install CUDA version (for RTX 40-series)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# OR for older RTX cards (30-series, 20-series)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 5. Install Other Dependencies

```bash
pip install -r requirements.txt
```

## Verify GPU Setup

Create `test_gpu.py` in `Trainer-Agent/agent/`:

```python
import torch

print("="*60)
print("PyTorch GPU Detection Test")
print("="*60)

print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    print(f"GPU count: {torch.cuda.device_count()}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    
    # Test GPU
    print("\nTesting GPU...")
    x = torch.rand(1000, 1000).cuda()
    y = torch.rand(1000, 1000).cuda()
    z = torch.matmul(x, y)
    print(f"✅ GPU test successful: {z.device}")
    print(f"✅ Result shape: {z.shape}")
else:
    print("\n❌ CUDA not available")
    print("The agent will use CPU (training will be much slower)")
    print("\nTo fix:")
    print("1. Install NVIDIA GPU drivers")
    print("2. Install CUDA toolkit")
    print("3. Reinstall PyTorch with CUDA:")
    print("   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")

print("\n" + "="*60)
```

Run:
```bash
python test_gpu.py
```

Expected output for RTX GPU:
```
============================================================
PyTorch GPU Detection Test
============================================================

PyTorch version: 2.6.0+cu121
CUDA available: True
CUDA version: 12.1
GPU device: NVIDIA GeForce RTX 4090
GPU count: 1
GPU memory: 24.00 GB

Testing GPU...
✅ GPU test successful: cuda:0
✅ Result shape: torch.Size([1000, 1000])

============================================================
```

## Performance Optimization for RTX GPU

### Optional: Enable Mixed Precision Training

**File**: `Trainer-Agent/agent/training/trainer.py` (line ~40)

```python
# Change from:
use_amp: bool = False

# To:
use_amp: bool = True  # 2-3x faster on RTX GPU
```

### Optional: Increase Batch Size

**File**: `Trainer-Agent/agent/config.py` (line ~20)

```python
# For RTX 4090 (24GB VRAM)
batch_size: int = 128

# For RTX 4080 (16GB VRAM)
batch_size: int = 96

# For RTX 4070 (12GB VRAM)
batch_size: int = 64  # Keep default
```

## Testing the Agent

### 1. Start the Agent

```bash
cd Trainer-Agent/agent
python main.py
```

Expected output:
```
Training Agent starting up...
Log level: INFO
GCP Bucket: your-bucket
Supabase URL: https://your-project.supabase.co
Automatic polling service started
[2025-11-10 ...] Polling service started (interval: 10s)
✅ Using NVIDIA GPU (CUDA)
INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
```

### 2. Test Health Check

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

### 3. Test Polling Status

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

## Integration with MCP Server

### Update MCP Server .env

**File**: `mcp_server/.env`

Add:
```bash
TRAINING_AGENT_URL=http://localhost:8003
```

### Update MCP Server Code

The MCP Server should already have endpoints to trigger training, but verify:

**File**: `mcp_server/main.py`

Should have something like:
```python
@app.post("/api/training/trigger")
async def trigger_training(project_id: str):
    # Call Training Agent
    response = requests.post(
        f"{TRAINING_AGENT_URL}/agents/training/start",
        json={"project_id": project_id}
    )
    return response.json()
```

## How It Works

### Auto-Polling Workflow

1. **Polling Service** checks database every 10 seconds
2. Finds projects with status `pending_training`
3. Triggers training automatically
4. After training completes, status → `pending_evaluation`
5. Polling service finds `pending_evaluation` projects
6. Triggers evaluation automatically
7. After evaluation, status → `completed`

### Training Workflow

```
pending_training
    ↓
Download dataset from GCP
    ↓
Extract & validate structure
    ↓
Auto-split if needed (train/val/test)
    ↓
Count classes
    ↓
Initialize model (ResNet/MobileNet/EfficientNet)
    ↓
Train with PyTorch (GPU accelerated)
    ↓
Upload model to GCP
    ↓
Update database
    ↓
pending_evaluation
```

### Evaluation Workflow

```
pending_evaluation
    ↓
Download model & dataset from GCP
    ↓
Load model
    ↓
Run inference on test set
    ↓
Compute metrics (accuracy, precision, recall, F1)
    ↓
Create user bundle:
  - model.pth
  - predict.py
  - labels.json
  - README.txt
    ↓
Upload bundle to GCP
    ↓
Update database with metrics
    ↓
completed
```

## Troubleshooting

### GPU Not Detected

**Problem**: Agent shows "Using CPU"

**Solution**:
1. Check NVIDIA drivers: `nvidia-smi`
2. Check CUDA installation
3. Reinstall PyTorch with CUDA:
   ```bash
   pip uninstall torch torchvision
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```
4. Run `test_gpu.py` to verify

### Port Already in Use

**Problem**: `Address already in use`

**Solution**:
1. Check if MCP Server is running on port 8003
2. Change port in `main.py` to 8004 or another free port
3. Update MCP Server's `TRAINING_AGENT_URL` accordingly

### Out of Memory (OOM)

**Problem**: `CUDA out of memory`

**Solution**:
1. Reduce batch size in `config.py`:
   ```python
   batch_size: int = 32  # or 16
   ```
2. Use smaller model:
   ```python
   preferred_model = "mobilenet_v2"  # instead of resnet50
   ```

### Temp Directory Errors

**Problem**: `No such file or directory: '/tmp/...'`

**Solution**:
- Apply the Windows temp directory fixes above
- Use `tempfile.gettempdir()` instead of `/tmp/`

## Summary

### ✅ What's Ready

- GPU support (CUDA)
- Auto-polling (both training & evaluation)
- Pretrained models
- Data augmentation
- Comprehensive evaluation
- User bundle creation

### 🔧 What Needs Fixing

1. Port: 8000 → 8003
2. Temp paths: `/tmp/` → `tempfile.gettempdir()`
3. PyTorch: Install CUDA version
4. .env: Create configuration file

### 🚀 Performance Tips

- Enable mixed precision (2-3x faster)
- Increase batch size (better GPU utilization)
- Use torch.compile (already enabled)
- Monitor GPU usage with `nvidia-smi`

## Next Steps

1. Apply the code changes above
2. Install PyTorch with CUDA
3. Create `.env` file
4. Test GPU detection
5. Start the agent
6. Test with a real project
7. Monitor logs and GPU usage
