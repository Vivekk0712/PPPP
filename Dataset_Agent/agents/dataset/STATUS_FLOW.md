# Project Status Flow

## Correct Status Progression

```
draft
  ↓
pending_dataset  ← Planner Agent sets this
  ↓
pending_training ← Dataset Agent sets this ✅
  ↓
training         ← Training Agent sets this (while training)
  ↓
pending_evaluation ← Training Agent sets this (after training)
  ↓
completed        ← Evaluation Agent sets this
```

## Dataset Agent Behavior

The Dataset Agent **ALWAYS** sets status to `pending_training` after:
1. ✅ Downloading dataset from Kaggle
2. ✅ Uploading to GCP bucket
3. ✅ Recording metadata in Supabase

### Code Locations:
- Line ~313: `"status": "pending_training"` (manual endpoint)
- Line ~507: `"status": "pending_training"` (auto-polling)

## If You See `training` Instead

This means:
- ❌ **NOT** set by Dataset Agent
- ✅ **SET BY** Training Agent (when it starts training)

### Training Agent Should:
1. Watch for `status = 'pending_training'`
2. Start training
3. Set `status = 'training'` (while training)
4. Set `status = 'pending_evaluation'` (after training)

## Verification

### Check a specific project:
```bash
python verify_status_updates.py <project-id>
```

### Check all projects:
```bash
python verify_status_updates.py
```

### Check in Supabase:
```sql
-- See all status transitions
SELECT 
    p.name,
    p.status,
    p.updated_at,
    al.agent_name,
    al.message
FROM projects p
LEFT JOIN agent_logs al ON p.id = al.project_id
WHERE p.id = 'your-project-id'
ORDER BY al.created_at DESC;
```

## Common Issues

### Issue: Status is `training` but training stopped
**Cause:** Training Agent set status to `training` but crashed/stopped

**Fix:** Manually reset in Supabase:
```sql
UPDATE projects
SET status = 'pending_training'
WHERE id = 'your-project-id';
```

### Issue: Status stuck at `pending_dataset`
**Cause:** Dataset Agent hasn't processed it yet or failed

**Fix:** Check agent logs:
```bash
python verify_status_updates.py <project-id>
```

## Dataset Agent Status Updates

The Dataset Agent sets these statuses:

| Status | When | Why |
|--------|------|-----|
| `pending_training` | Success | Dataset uploaded, ready for training |
| `failed` | Error | Dataset download/upload failed |

**NEVER sets:** `training`, `pending_evaluation`, `completed`

Those are set by Training Agent and Evaluation Agent respectively.
