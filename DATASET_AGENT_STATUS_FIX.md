# Dataset Agent Status Update Fix

## Problem Identified

The Dataset Agent was marking projects as `failed` even when the dataset was successfully uploaded to GCP. This happened because:

1. ✅ Dataset downloads from Kaggle successfully
2. ✅ Dataset uploads to GCP bucket successfully  
3. ✅ Dataset info is stored in Supabase `datasets` table
4. ❌ **Status update to `pending_training` fails** (network issue, DB connection, etc.)
5. ❌ Exception handler catches the error and marks project as `failed`

**Result**: Dataset is in GCP and database, but project shows as "failed" instead of "pending_training"

## Root Cause

The exception handler was too aggressive - it marked ANY error as a complete failure, even if the core work (dataset upload) was successful.

```python
# OLD CODE - Too aggressive
except Exception as e:
    log_to_supabase(project_id, f"Error: {str(e)}", "error")
    supabase.table("projects").update({
        "status": "failed",  # ❌ Marks as failed even if dataset uploaded
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", project_id).execute()
    raise HTTPException(status_code=500, detail=str(e))
```

## Solution Implemented

### 1. Retry Logic for Status Updates

Added retry mechanism (3 attempts with 2-second delays) for status updates:

```python
# NEW CODE - Retry status updates
max_retries = 3
for attempt in range(max_retries):
    try:
        update_result = supabase.table("projects").update({
            "status": "pending_training",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", project_id).execute()
        status_updated = True
        break
    except Exception as status_error:
        if attempt < max_retries - 1:
            time.sleep(2)  # Wait before retry
        else:
            # Log warning but don't fail the whole operation
            log_to_supabase(project_id, "Dataset uploaded but status update failed", "warning")
```

### 2. Smart Exception Handling

Exception handler now checks if dataset was uploaded before marking as failed:

```python
# NEW CODE - Check dataset before marking failed
except Exception as e:
    # Check if dataset exists
    dataset_check = supabase.table("datasets").select("*").eq("project_id", project_id).execute()
    
    if dataset_check.data:
        # Dataset exists - don't mark as failed!
        print("⚠️ Error occurred but dataset was uploaded. Not marking as failed.")
        log_to_supabase(project_id, "Dataset uploaded but error in post-processing", "warning")
    else:
        # No dataset - this is a real failure
        supabase.table("projects").update({
            "status": "failed",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", project_id).execute()
```

### 3. User Notifications

If status update fails but dataset is uploaded, user gets a warning message:

```python
send_chat_message(user_id, 
    f"⚠️ Dataset uploaded successfully but status update failed.\n"
    f"Dataset: {dataset_ref}\n"
    f"Size: {file_size_gb:.2f} GB\n"
    f"Please contact support to update project status.")
```

## Changes Made

### Files Modified
- `Dataset_Agent/agents/dataset/main.py`

### Functions Updated
1. `start_dataset_job()` - Main endpoint handler
2. `process_project_sync()` - Auto-polling handler

### Key Improvements
- ✅ Retry logic for status updates (3 attempts)
- ✅ Smart exception handling (checks if dataset exists)
- ✅ Better logging (info/warning/error levels)
- ✅ User notifications for partial failures
- ✅ Prevents false "failed" status when dataset is uploaded

## Testing

To test the fix:

1. Start the Dataset Agent:
   ```bash
   cd Dataset_Agent/agents/dataset
   python main.py
   ```

2. Create a test project with status `pending_dataset`

3. Monitor the logs - you should see:
   - Dataset download ✅
   - GCP upload ✅
   - Dataset info stored ✅
   - Status update attempts (with retries if needed)
   - Final status: `pending_training` (not `failed`)

## Manual Status Fix (If Needed)

If you have projects stuck with `failed` status but dataset exists:

```python
# Check for datasets with failed projects
SELECT p.id, p.name, p.status, d.name as dataset_name
FROM projects p
JOIN datasets d ON p.id = d.project_id
WHERE p.status = 'failed';

# Fix the status
UPDATE projects 
SET status = 'pending_training', updated_at = NOW()
WHERE id = '<project_id>';
```

## Prevention

This fix prevents the issue by:
1. **Retrying** transient failures (network glitches, timeouts)
2. **Not failing** when the core work (dataset upload) is complete
3. **Logging warnings** instead of errors for post-processing issues
4. **Notifying users** when manual intervention is needed

## Next Steps

- Monitor agent logs for any "warning" level messages
- If status updates consistently fail, investigate database connection issues
- Consider adding a background job to auto-fix stuck projects with uploaded datasets
