# 🤖 Planner Agent - Automation Guide

Complete guide for automated project creation and pipeline integration.

## 🎯 Overview

The Planner Agent now supports **fully automated** project creation:
1. You submit a simple text prompt
2. Gemini LLM parses your intent
3. Project plan is created and stored in Supabase
4. Status set to `pending_dataset`
5. Dataset Agent (architecture2.md) automatically picks it up
6. Pipeline continues through Training → Evaluation

## 🚀 Quick Start

### Method 1: Interactive Mode (Recommended)

```bash
# Make sure Planner Agent is running
py main.py

# In another terminal, start interactive mode
py auto_planner.py
```

Then just type your prompts:
```
💬 Enter your prompt: Train a model to classify tomato diseases
✅ SUCCESS! Project Created
   Project ID: abc-123-def
   Name: Tomato Disease Classifier
   Status: pending_dataset (ready for Dataset Agent)
```

### Method 2: Quick Submit (Single Command)

```bash
py quick_submit.py "Train a model for plant disease detection"
```

### Method 3: Batch Processing

```bash
# Process multiple prompts at once
py batch_process.py
```

Edit `batch_process.py` to add your own prompts to the `EXAMPLE_PROMPTS` list.

## 📋 Usage Examples

### Example Prompts

```bash
# Plant disease detection
py quick_submit.py "Train a PyTorch model to classify tomato leaf diseases"

# Medical imaging
py quick_submit.py "Build a chest X-ray pneumonia detector"

# Animal classification
py quick_submit.py "Create a cat vs dog image classifier"

# Skin cancer detection
py quick_submit.py "Detect melanoma from dermoscopy images"

# Crop disease
py quick_submit.py "Classify wheat rust disease from leaf photos"
```

## 🔄 How the Pipeline Works

```
┌─────────────────────────────────────────────────────────────┐
│ 1. YOU: Submit Prompt                                       │
│    "Train a model for plant disease detection"             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PLANNER AGENT (architecture1.md)                         │
│    ✓ Gemini LLM parses intent                              │
│    ✓ Creates structured project plan                       │
│    ✓ Stores in Supabase: status='pending_dataset'         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. DATASET AGENT (architecture2.md) - AUTO TRIGGERED        │
│    ✓ Polls Supabase for pending_dataset projects          │
│    ✓ Downloads dataset from Kaggle                        │
│    ✓ Uploads to GCP bucket                                │
│    ✓ Updates status='pending_training'                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. TRAINING AGENT (architecture3.md) - AUTO TRIGGERED       │
│    ✓ Polls for pending_training projects                  │
│    ✓ Downloads dataset from GCP                           │
│    ✓ Trains PyTorch model                                 │
│    ✓ Uploads model to GCP                                 │
│    ✓ Updates status='pending_evaluation'                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. EVALUATION AGENT (architecture4.md) - AUTO TRIGGERED     │
│    ✓ Polls for pending_evaluation projects                │
│    ✓ Evaluates model on test data                         │
│    ✓ Computes accuracy and metrics                        │
│    ✓ Updates status='completed'                           │
│    ✓ Sends results to user                                │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Change Test User

Edit the `TEST_USER_ID` in the automation scripts:

```python
# In auto_planner.py, batch_process.py, quick_submit.py
TEST_USER_ID = "your-user-id-here"
```

### Change Planner URL

```python
PLANNER_URL = "http://localhost:8001"  # Change if running on different port
```

## 📊 Monitoring

### Check Projects in Supabase

```sql
-- View all projects
SELECT id, name, status, created_at 
FROM projects 
ORDER BY created_at DESC;

-- View pending projects
SELECT id, name, status 
FROM projects 
WHERE status = 'pending_dataset';

-- View agent logs
SELECT agent_name, message, log_level, created_at 
FROM agent_logs 
ORDER BY created_at DESC 
LIMIT 20;
```

### Check via API

```bash
# Get project details
curl http://localhost:8001/agents/planner/project/{project_id}

# Health check
curl http://localhost:8001/health
```

## 🎬 Complete Workflow Example

### Step 1: Start Planner Agent

```bash
cd agent/planner
py main.py
```

### Step 2: Submit Prompts

**Option A: Interactive**
```bash
py auto_planner.py
# Then type prompts interactively
```

**Option B: Quick Submit**
```bash
py quick_submit.py "Train a model for tomato disease detection"
py quick_submit.py "Build a chest X-ray classifier"
py quick_submit.py "Create a cat vs dog detector"
```

**Option C: Batch**
```bash
py batch_process.py
```

### Step 3: Verify in Supabase

Check that projects are created with `status='pending_dataset'`

### Step 4: Dataset Agent Picks Up

Your teammate's Dataset Agent (architecture2.md) should automatically:
- Poll Supabase for `status='pending_dataset'`
- Process each project
- Update status to `pending_training`

### Step 5: Continue Through Pipeline

Training Agent → Evaluation Agent → Completed!

## 🐛 Troubleshooting

### "Cannot connect to Planner Agent"

Make sure the agent is running:
```bash
py main.py
```

### "User ID not found"

Create a test user:
```bash
py create_test_user.py
```

Then update the `TEST_USER_ID` in automation scripts.

### "Gemini API Error"

Check your `.env` file has valid `GEMINI_API_KEY`

### Projects not being picked up by Dataset Agent

Verify:
1. Projects have `status='pending_dataset'` in Supabase
2. Dataset Agent is running and polling
3. Dataset Agent is checking the correct Supabase table

## 📝 Integration with Other Agents

### For Dataset Agent (Member 2)

Your Dataset Agent should poll like this:

```python
# Poll for new projects
while True:
    result = supabase.table("projects")\
        .select("*")\
        .eq("status", "pending_dataset")\
        .execute()
    
    for project in result.data:
        # Process project
        download_dataset(project)
        upload_to_gcp(project)
        
        # Update status
        supabase.table("projects")\
            .update({"status": "pending_training"})\
            .eq("id", project["id"])\
            .execute()
    
    time.sleep(10)  # Check every 10 seconds
```

### For Training Agent (Member 3)

Poll for `status='pending_training'`

### For Evaluation Agent (Member 4)

Poll for `status='pending_evaluation'`

## 🎯 Best Practices

1. **Keep Planner Agent Running**: Run `py main.py` in a dedicated terminal
2. **Use Interactive Mode**: `auto_planner.py` for testing multiple prompts
3. **Use Quick Submit**: For single prompts in scripts/automation
4. **Monitor Logs**: Check `agent_logs` table in Supabase
5. **Verify Status**: Ensure each agent updates status correctly

## 🚀 Production Deployment

For production, consider:

1. **Run as Service**: Use systemd/supervisor to keep agent running
2. **Add Queue**: Use Redis/RabbitMQ for better scalability
3. **Add Webhooks**: Notify agents instead of polling
4. **Add Monitoring**: Use Prometheus/Grafana for metrics
5. **Add Rate Limiting**: Prevent API abuse

## 📚 Related Files

- `main.py` - Main Planner Agent service
- `auto_planner.py` - Interactive automation mode
- `quick_submit.py` - Single command submission
- `batch_process.py` - Batch processing
- `test_manual.py` - Manual testing
- `create_test_user.py` - Create test user in Supabase

## ✅ Success Checklist

- [ ] Planner Agent running on port 8001
- [ ] Test user created in Supabase
- [ ] Can submit prompts via automation scripts
- [ ] Projects appear in Supabase with correct status
- [ ] Dataset Agent picks up projects automatically
- [ ] Full pipeline works end-to-end

---

**You're all set!** Just submit prompts and watch the magic happen! 🎉
