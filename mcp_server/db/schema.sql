-- users
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  firebase_uid text unique not null,
  email text,
  name text,
  created_at timestamptz default now()
);

-- messages
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  role text not null, -- 'user' | 'assistant' | 'system'
  content text not null,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

-- optional embeddings table
create table if not exists embeddings (
  id uuid primary key default gen_random_uuid(),
  message_id uuid references messages(id) on delete cascade,
  vector double precision[] -- or use pgvector if enabled
);
