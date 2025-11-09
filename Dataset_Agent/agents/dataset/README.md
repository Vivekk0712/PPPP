# Dataset Agent

The Dataset Agent handles dataset discovery, download from Kaggle, and upload to GCP bucket.

## Features

- Kaggle API authentication
- Dataset search based on project keywords
- Automatic download and upload to GCP
- Supabase integration for metadata storage
- Status updates and logging

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Set up GCP credentials:
- Download service account JSON from GCP Console
- Set `GOOGLE_APPLICATION_CREDENTIALS` to the file path

4. Run the agent:
```bash
python main.py
```

The agent will start on `http://localhost:8001`

## API Endpoints

### POST /agents/dataset/start
Start dataset discovery and upload for a project.

**Request:**
```json
{
  "project_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "dataset_name": "dataset-ref",
  "gcs_url": "gs://bucket/raw/dataset.zip",
  "size": "4.20 GB"
}
```

### POST /agents/dataset/auth
Save Kaggle credentials for a project.

**Request:**
```json
{
  "project_id": "uuid",
  "kaggle_username": "your-username",
  "kaggle_key": "your-api-key"
}
```

### GET /agents/dataset/status/{project_id}
Get dataset status and logs for a project.

### GET /health
Health check endpoint. Returns polling status.

### POST /agents/dataset/polling/start
Manually start auto-polling (if not started on startup).

### POST /agents/dataset/polling/stop
Stop auto-polling.

## Workflow

### Auto-Polling Mode (Default)
The agent automatically watches Supabase for projects with `status='pending_dataset'` and processes them:

1. Agent polls Supabase every 10 seconds (configurable)
2. Finds projects with status `pending_dataset`
3. For each project:
   - Checks for Kaggle credentials in project metadata
   - Authenticates with Kaggle API (creates temporary `~/.kaggle/kaggle.json`)
     - Windows: `C:\Users\<username>\.kaggle\kaggle.json`
     - Linux/Mac: `~/.kaggle/kaggle.json`
   - Searches for dataset using project keywords
   - Downloads dataset to temporary directory
   - Uploads to GCP bucket at `raw/{dataset-name}.zip`
   - Records metadata in Supabase `datasets` table
   - Updates project status to `pending_training`
   - Cleans up temporary files and Kaggle credentials

### Manual Mode
You can also trigger processing manually via API endpoints.

## Security Notes

- Kaggle credentials are stored temporarily in project metadata
- Credentials are deleted from filesystem after use
- Use GCP service account with minimal permissions (upload only)
- Validate all inputs before processing
