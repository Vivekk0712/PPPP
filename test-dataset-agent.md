# Dataset Agent Troubleshooting Guide

## Check Dataset Agent Logs

Look at the Dataset Agent terminal for the full error. The 500 error could be caused by:

### 1. Kaggle Authentication Error
**Symptoms:**
- Error mentions "Kaggle" or "authentication"
- Error about API key

**Fix:**
```bash
# Check if Kaggle credentials are valid
# In Dataset Agent terminal, you should see:
# "Authenticating with Kaggle"
```

### 2. GCP Upload Error
**Symptoms:**
- Error mentions "GCP", "storage", or "bucket"
- Error about credentials or permissions

**Fix:**
- Check if `C:\Users\Dell\credentials\service-account.json` exists
- Verify GCP bucket `automl-datasets-vivek` exists
- Check service account has Storage Admin role

### 3. Kaggle Dataset Not Found
**Symptoms:**
- Error: "No suitable dataset found"
- Kaggle search returns empty

**Fix:**
- Keywords might be too specific
- Try with simpler keywords

### 4. Missing Dependencies
**Symptoms:**
- ImportError or ModuleNotFoundError

**Fix:**
```bash
cd Dataset_Agent/agents/dataset
pip install -r requirements.txt
```

## Manual Test

Test the Dataset Agent directly:

```bash
curl -X POST http://127.0.0.1:8002/agents/dataset/start \
  -H "Content-Type: application/json" \
  -d "{\"project_id\":\"YOUR_PROJECT_ID_HERE\"}"
```

Replace `YOUR_PROJECT_ID_HERE` with an actual project ID from your database.

## Check Dataset Agent Terminal

Look for these log messages in order:
1. ✅ "Starting dataset agent"
2. ✅ "Authenticating with Kaggle"
3. ✅ "Searching for dataset with keywords: [...]"
4. ✅ "Found dataset: ..."
5. ✅ "Downloading dataset: ..."
6. ✅ "Uploading to GCP..."
7. ✅ "Dataset uploaded successfully"

**Where does it fail?** That's where the problem is!

## Common Errors & Solutions

### Error: "Kaggle API credentials not found"
**Solution:**
```env
# Add to Dataset_Agent/agents/dataset/.env
KAGGLE_USERNAME=your-username
KAGGLE_KEY=your-api-key
```

### Error: "Could not find credentials"
**Solution:**
- Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- File should exist at that location
- File should be valid JSON

### Error: "Bucket not found"
**Solution:**
- Create GCP bucket: `gsutil mb gs://automl-datasets-vivek`
- Or update `.env` with correct bucket name

### Error: "No datasets found"
**Solution:**
- Keywords might be too specific
- Check Kaggle manually: https://www.kaggle.com/datasets
- Search with your keywords to see if datasets exist

## Quick Fix: Disable Auto-Trigger

If Dataset Agent keeps failing, you can disable auto-trigger temporarily:

In `mcp_server/main.py`, comment out the Dataset Agent trigger:

```python
# Automatically trigger Dataset Agent to start processing
# try:
#     import asyncio
#     await asyncio.sleep(0.5)
#     ...
# except Exception as e:
#     logger.warning(f"Could not trigger Dataset Agent: {str(e)}")
```

Then manually trigger it after fixing the issue.

## Next Steps

1. **Check Dataset Agent terminal** for full error
2. **Identify which step fails** (auth, search, download, upload)
3. **Fix that specific issue**
4. **Test again**

## Need the Full Error?

Run this in Dataset Agent terminal to see detailed errors:

```bash
cd Dataset_Agent/agents/dataset
venv\Scripts\activate
python -c "import sys; print(sys.path)"
uvicorn main:app --reload --port 8002 --log-level debug
```

This will show more detailed error messages.
