# AutoML Platform - Setup Guide

## Prerequisites
- Node.js 16+ and npm
- Python 3.10+
- Firebase project with authentication enabled
- Supabase project
- Google Cloud Platform account (for storage)

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
npm install
```

### 2. Configure Environment Variables
Create `backend/.env`:
```env
PORT=4000
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./serviceAccount.json
SESSION_COOKIE_NAME=__session
SESSION_EXPIRES_IN=432000000
NODE_ENV=development
MCP_SERVER_URL=http://127.0.0.1:8000
```

### 3. Add Firebase Service Account
- Download service account JSON from Firebase Console
- Save as `backend/serviceAccount.json`

### 4. Start Backend Server
```bash
npm start
```
Server runs on http://localhost:4000

## MCP Server Setup

### 1. Create Virtual Environment
```bash
cd mcp_server
python -m venv venv
```

### 2. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn supabase google-cloud-storage torch torchvision pydantic pydantic-settings python-dotenv
```

### 4. Configure Environment Variables
Create `mcp_server/.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
GEMINI_API_KEY=your-gemini-api-key
GCP_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/gcp-service-account.json
```

### 5. Start MCP Server
```bash
uvicorn main:app --reload
```
Server runs on http://127.0.0.1:8000

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment Variables
Create `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:4000
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

### 3. Start Development Server
```bash
npm run dev
```
Frontend runs on http://localhost:5173

## Supabase Database Setup

### 1. Create Tables

Run these SQL commands in Supabase SQL Editor:

```sql
-- Users table (existing)
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  firebase_uid text unique not null,
  email text,
  name text,
  created_at timestamptz default now()
);

-- Messages table (existing)
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  role text not null,
  content text not null,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

-- Projects table (NEW)
create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  name text not null,
  task_type text not null,
  framework text default 'pytorch',
  dataset_source text default 'kaggle',
  search_keywords text[],
  status text default 'draft',
  accuracy numeric,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Datasets table (NEW)
create table if not exists datasets (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id) on delete cascade,
  name text,
  gcs_url text,
  size text,
  source text default 'kaggle',
  created_at timestamptz default now()
);

-- Models table (NEW)
create table if not exists models (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id) on delete cascade,
  name text,
  framework text default 'pytorch',
  gcs_url text,
  accuracy numeric,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

-- Agent logs table (NEW)
create table if not exists agent_logs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id) on delete cascade,
  agent_name text,
  message text,
  log_level text default 'info',
  created_at timestamptz default now()
);
```

### 2. Enable Row Level Security (Optional)
```sql
-- Enable RLS on projects table
alter table projects enable row level security;

-- Policy: Users can only see their own projects
create policy "Users can view own projects"
  on projects for select
  using (auth.uid()::text = user_id::text);

-- Repeat for other tables as needed
```

## Google Cloud Platform Setup

### 1. Create Storage Bucket
```bash
gsutil mb gs://your-bucket-name
```

### 2. Set Bucket Structure
```
gs://your-bucket-name/
├── raw/           # Raw datasets
├── models/        # Trained models
└── exports/       # Model bundles for download
```

### 3. Create Service Account
- Go to GCP Console → IAM & Admin → Service Accounts
- Create new service account
- Grant "Storage Object Admin" role
- Download JSON key
- Save as specified in environment variables

## Testing the Setup

### 1. Test Backend
```bash
curl http://localhost:4000/api/me
```

### 2. Test MCP Server
```bash
curl http://localhost:8000/health
```

### 3. Test Frontend
- Open http://localhost:5173
- Sign in with Google/Email/Phone
- Navigate to ML Projects tab
- Create a test project

## Common Issues

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :4000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:4000 | xargs kill -9
```

### CORS Errors
- Ensure backend CORS settings include frontend URL
- Check that credentials are enabled

### Supabase Connection Issues
- Verify SUPABASE_URL and keys are correct
- Check if service role key has proper permissions
- Ensure tables are created

### Firebase Auth Issues
- Verify Firebase config in frontend .env
- Check Firebase Console for enabled auth methods
- Ensure service account JSON is valid

## Development Workflow

1. Start MCP Server (Terminal 1)
2. Start Backend Server (Terminal 2)
3. Start Frontend Dev Server (Terminal 3)
4. Make changes and test
5. Check logs in all terminals for errors

## Production Deployment

### Backend
- Deploy to services like Railway, Render, or Heroku
- Set environment variables in platform
- Update CORS origins

### Frontend
- Build: `npm run build`
- Deploy to Netlify, Vercel, or similar
- Update API_BASE_URL to production backend

### MCP Server
- Deploy to cloud VM or container service
- Ensure Python dependencies are installed
- Set up process manager (PM2, systemd)

## Next Steps

1. Implement actual AI agents (Planner, Dataset, Training, Evaluation)
2. Connect to real Kaggle API for datasets
3. Implement model training pipeline
4. Add model download functionality
5. Implement image testing with trained models
6. Add real-time status updates
7. Enhance error handling and logging

## Support

For issues or questions:
- Check logs in all three services
- Review Supabase dashboard for data
- Check Firebase Console for auth issues
- Verify all environment variables are set correctly
