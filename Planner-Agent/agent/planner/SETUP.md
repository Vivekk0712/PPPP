# 🚀 Planner Agent - Setup Guide

Complete setup instructions for the Planner Agent.

## ✅ Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.10 or higher installed
- [ ] pip package manager
- [ ] Supabase account and project created
- [ ] Google Gemini API key
- [ ] Database tables created in Supabase

## 📋 Step-by-Step Setup

### Step 1: Database Setup

Run this SQL in your Supabase SQL Editor:

```sql
-- Create projects table
create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  name text not null,
  task_type text not null,
  framework text default 'pytorch',
  dataset_source text default 'kaggle',
  search_keywords text[],
  status text default 'draft',
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Create agent_logs table
create table if not exists agent_logs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id) on delete cascade,
  agent_name text,
  message text,
  log_level text default 'info',
  created_at timestamptz default now()
);

-- Create indexes for performance
create index idx_projects_status on projects(status);
create index idx_projects_user_id on projects(user_id);
create index idx_agent_logs_project_id on agent_logs(project_id);
```

### Step 2: Get API Keys

#### Supabase
1. Go to your Supabase project dashboard
2. Navigate to Settings > API
3. Copy your project URL and anon/service key

#### Google Gemini
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key

### Step 3: Install Dependencies

```bash
cd agent/planner

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
# Use notepad, vim, or any text editor
notepad .env
```

Fill in these values in `.env`:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GEMINI_API_KEY=AIzaSy...
LOG_LEVEL=INFO
```

### Step 5: Test the Setup

```bash
# Start the agent
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Step 6: Verify It Works

Open a new terminal and run:

```bash
# Test health endpoint
curl http://localhost:8001/health

# Or use the test script
python test_manual.py
```

## 🧪 Testing

### Quick Test
```bash
python test_manual.py
```

### Unit Tests
```bash
pip install pytest pytest-mock
pytest test_planner.py -v
```

### Manual API Test
```bash
curl -X POST http://localhost:8001/agents/planner/handle_message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "session_id": "test-session-456",
    "message_text": "Train a model for plant disease detection"
  }'
```

## 🐛 Troubleshooting

### Issue: "Module not found" errors
**Solution:** Make sure you activated the virtual environment and installed dependencies
```bash
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Issue: "Connection refused" to Supabase
**Solution:** 
- Check your `SUPABASE_URL` is correct
- Verify your `SUPABASE_KEY` is valid
- Test connection: `curl https://your-project.supabase.co`

### Issue: Gemini API errors
**Solution:**
- Verify your `GEMINI_API_KEY` is correct
- Check API quota at https://makersuite.google.com
- Ensure you have billing enabled if required

### Issue: "Table does not exist"
**Solution:** Run the SQL schema from Step 1 in Supabase SQL Editor

### Issue: Port 8001 already in use
**Solution:** 
```bash
# Find and kill the process
# Windows:
netstat -ano | findstr :8001
taskkill /PID <process_id> /F

# Or use a different port
uvicorn main:app --port 8002
```

## 🔍 Verify Database

After running a test, check Supabase:

```sql
-- Check projects created
SELECT * FROM projects ORDER BY created_at DESC LIMIT 5;

-- Check agent logs
SELECT * FROM agent_logs WHERE agent_name = 'planner' ORDER BY created_at DESC LIMIT 10;

-- Check messages sent
SELECT * FROM messages WHERE role = 'assistant' ORDER BY created_at DESC LIMIT 5;
```

## 🚀 Production Deployment

### Using Docker

```bash
# Build image
docker build -t planner-agent .

# Run container
docker run -p 8001:8001 --env-file .env planner-agent
```

### Using systemd (Linux)

Create `/etc/systemd/system/planner-agent.service`:
```ini
[Unit]
Description=Planner Agent
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/agent/planner
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable planner-agent
sudo systemctl start planner-agent
sudo systemctl status planner-agent
```

## 📊 Monitoring

### Check Logs
```bash
# Application logs
tail -f logs/planner.log

# Or check Supabase agent_logs table
```

### Health Monitoring
```bash
# Simple health check
curl http://localhost:8001/health

# With monitoring tool
watch -n 5 'curl -s http://localhost:8001/health | jq'
```

## 🔐 Security Checklist

- [ ] Never commit `.env` file to git
- [ ] Use service role key only in secure environments
- [ ] Enable Row Level Security (RLS) in Supabase
- [ ] Rotate API keys regularly
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Validate all user inputs

## 📚 Next Steps

1. ✅ Planner Agent is running
2. ⏭️ Set up Dataset Agent (Member 2)
3. ⏭️ Set up Training Agent (Member 3)
4. ⏭️ Set up Evaluation Agent (Member 4)
5. ⏭️ Integrate with MCP Server

## 🆘 Getting Help

- Check `README.md` for usage examples
- Review `architecture.md` for design details
- Check Supabase `agent_logs` table for errors
- Review application logs for stack traces

## ✅ Success Criteria

You've successfully set up the Planner Agent when:
- [ ] Health endpoint returns 200 OK
- [ ] Test message creates project in Supabase
- [ ] Agent logs appear in `agent_logs` table
- [ ] Chat reply appears in `messages` table
- [ ] Project status is set to `pending_dataset`
