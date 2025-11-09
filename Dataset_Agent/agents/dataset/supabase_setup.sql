-- Supabase Setup SQL for Dataset Agent Testing
-- Run these queries in your Supabase SQL Editor

-- 1. Create tables (if not already created)
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text unique,
  created_at timestamptz default now()
);

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

create table if not exists datasets (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id) on delete cascade,
  name text,
  gcs_url text,
  size text,
  source text default 'kaggle',
  created_at timestamptz default now()
);

create table if not exists agent_logs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id) on delete cascade,
  agent_name text,
  message text,
  log_level text default 'info',
  created_at timestamptz default now()
);

create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  role text not null,
  content text not null,
  created_at timestamptz default now()
);

-- 2. Insert a test user
insert into users (id, email) 
values ('00000000-0000-0000-0000-000000000001', 'test@example.com')
on conflict (email) do nothing;

-- 3. Insert a test project for Dataset Agent testing
insert into projects (
  id,
  user_id,
  name,
  task_type,
  framework,
  dataset_source,
  search_keywords,
  status,
  metadata
) values (
  '11111111-1111-1111-1111-111111111111',
  '00000000-0000-0000-0000-000000000001',
  'Intel Image Classification Test',
  'image_classification',
  'pytorch',
  'kaggle',
  ARRAY['intel', 'image', 'classification'],
  'pending_dataset',
  jsonb_build_object(
    'kaggle_credentials', jsonb_build_object(
      'username', 'YOUR_KAGGLE_USERNAME',
      'key', 'YOUR_KAGGLE_API_KEY'
    ),
    'max_dataset_size_gb', 5,
    'target_metric', 'accuracy',
    'target_value', 0.9
  )
)
on conflict (id) do update set
  status = 'pending_dataset',
  updated_at = now();

-- 4. Verify the data
select * from users where id = '00000000-0000-0000-0000-000000000001';
select * from projects where id = '11111111-1111-1111-1111-111111111111';
