Sprint 0 — Project setup & conventions (pre-work)
Story 0.1 — Create monorepo and branch strategy

Description: Initialize repository, create frontend/, backend/, mcp_server/ folders and basic README. Set main + dev branches.
Prereqs: git installed, project owner access
Steps:

Create repo and clone.

Create folders:

mkdir frontend backend mcp_server
git add . && git commit -m "scaffold"


Add .gitignore, LICENSE, CONTRIBUTING.md.

Define branch policy: main (prod), dev (integration), feature branches feat/....
Acceptance criteria: Repo has folder structure and docs.
DoD: Repo initialized, dev branch pushed.

Story 0.2 — Secrets & env management

Description: Decide how secrets will be stored for local/dev/prod (dotenv for local, secret manager / platform env for prod).
Prereqs: None
Steps:

Add .env.example listing: FIREBASE_SERVICE_ACCOUNT_PATH, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GEMINI_API_KEY, NODE_ENV.

Add instructions to README about using secret store (Vercel, Railway, Cloud Run).
Acceptance criteria: .env.example present and README explains secrets.
DoD: Team knows where to place keys.

Sprint 1 — Database (Supabase) & schema

These stories create the ground truth for user & message data.

Story 1.1 — Provision Supabase project and DB connectivity

Description: Create Supabase project, obtain SUPABASE_URL and SERVICE_ROLE_KEY.
Prereqs: Supabase account
Steps:

Create project in Supabase UI.

Copy SUPABASE_URL and SERVICE_ROLE_KEY into local .env.

Install CLI or use dashboard for table creation.
Acceptance criteria: Keys available and placed in .env.

Story 1.2 — Create DB schema (users, messages, preferences)

Description: Create tables required for chatbot context.
SQL (run in Supabase SQL editor):

-- users
create table if not exists users (
  id uuid primary key,
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


Notes: Because auth is Firebase (not Supabase Auth), do DB access server-side using SERVICE_ROLE_KEY. RLS can be added if later switching to Supabase Auth.
Acceptance criteria: Tables created and visible.

Sprint 2 — Node.js gateway (auth + routing)

The Node.js backend verifies Firebase tokens, acts as secure gateway and forwards chat requests to MCP server.

Story 2.1 — Scaffold Express gateway & Firebase verification

Description: Create backend/ Express app that verifies Firebase ID tokens on incoming requests.
Prereqs: Firebase Admin service account JSON
Steps:

cd backend → npm init -y

npm i express axios firebase-admin dotenv

Add utils/verifyFirebase.js to validate Authorization: Bearer <idToken> using firebase-admin.

Expose /api/health and protected /api/chat endpoints.
Sample verify middleware (concept):

// verifyFirebase.js
const admin = require('firebase-admin');
admin.initializeApp({ credential: admin.credential.cert(require(process.env.FIREBASE_SERVICE_ACCOUNT_PATH)) });

module.exports = async function verify(req, res, next) {
  const auth = req.headers.authorization?.split(' ')[1];
  if (!auth) return res.status(401).send({ error: 'no token' });
  try {
    const decoded = await admin.auth().verifyIdToken(auth);
    req.firebaseUid = decoded.uid;
    next();
  } catch(e) { res.status(401).send({ error: 'invalid token' }); }
}


Acceptance criteria: /api/health returns 200; /api/chat accepts requests with valid Firebase token.

Story 2.2 — Implement /api/chat to forward to MCP

Description: /api/chat receives message, validates token, and forwards to MCP server.
Steps:

Route receives { message, metadata? }.

Build payload:

{ "user_id": "<firebaseUid>", "message": "text", "metadata": {...} }


Forward to MCP server POST http://mcp-host:8000/mcp/query (use internal URL in prod).

Return MCP server response to frontend.
Acceptance criteria: Gateway forwards and returns MCP response unchanged (status 200).

Sprint 3 — Python MCP server skeleton & tools

Create a small FastAPI-based MCP server that exposes tools Gemini can use.

Story 3.1 — Scaffold FastAPI + dependencies

Description: Create mcp_server/ with FastAPI skeleton.
Prereqs: Python 3.10+, virtualenv
Steps:

python -m venv .venv && source .venv/bin/activate

pip install fastapi uvicorn httpx supabase client (and the Gemini client package you use, e.g. google-genai or genai if available).

Create main.py with /mcp/query and /health.
Sample startup command:

uvicorn main:app --host 0.0.0.0 --port 8000


Acceptance criteria: GET /health returns 200.

Story 3.2 — Implement Supabase connector (server-side)

Description: Add functions to read/write users and messages from Supabase using SERVICE_ROLE_KEY.
Steps:

Install supabase-py (or postgrest HTTP client).

Create supabase_client.py to expose get_or_create_user(firebase_uid, email, name), store_message(user_id, role, content, metadata), get_recent_messages(user_id, limit=10).
Acceptance criteria: Python functions can add/read rows from users and messages.

Story 3.3 — Define MCP tools (get_user_profile, get_chat_history, store_message)

Description: Define tool wrappers that Gemini can call via MCP.
Steps:

In tools/ create user_tools.py, chat_tools.py.

get_user_profile(firebase_uid) → returns user row (create if missing).

get_chat_history(firebase_uid, limit) → fetch last N messages and return ordered list.

store_message(firebase_uid, role, content) → persist message to DB.
Acceptance criteria: Tools work in isolation (unit-tested).

Sprint 4 — Gemini 2.5 Pro integration (LLM orchestration)

Make Gemini produce responses using context and tools.

Story 4.1 — Add Gemini client wrapper and prompt templates

Description: Create ai_client.py that wraps Gemini 2.5 Pro calls and supports structured inputs (system, user, context).
Prereqs: GEMINI_API_KEY
Steps:

Create ai_client.py with generate_from_prompt(prompt, context) function.

Provide prompt templating: include last N messages, user profile summary, and system instructions.

Keep prompts short — add “tool hint” lines when calling tools.
Acceptance criteria: Gemini returns text for sample prompts.

Implementation hint: Use JSON payloads to Gemini with fields system, messages, and optionally specify model: "gemini-2.5-pro".

Story 4.2 — Implement the contextual_reasoning orchestration logic

Description: Orchestrator decides when to call tools vs. call Gemini directly and builds the final response.
Steps:

When a /mcp/query arrives:

Fetch user profile.

Fetch last_n messages.

Build prompt: system + context + user message.

Optionally pre-process (intent detection) to decide tool usage (e.g., if user asks “show my last transactions”, call get_user_profile or DB).

Call Gemini to generate reply.

Store both user message and assistant reply via store_message.

Return structured response:

{ "reply": "...", "tools_called": ["get_chat_history"], "stored": true }


Acceptance criteria: End-to-end flow returns reply saved in DB.

Sprint 5 — Frontend chatbot UI & integration

Connect existing React app to backend + implement chat experience.

Story 5.1 — Chat UI + send auth header

Description: Build a ChatBot React component that sends messages to backend/api/chat including Firebase ID token.
Steps:

On login, obtain ID token:

const token = await firebase.auth().currentUser.getIdToken();


POST to /api/chat with header Authorization: Bearer ${token} and body { message }.

Display streaming or normal responses.
Acceptance criteria: Authenticated user gets replies in UI.

Story 5.2 — Message persistence confirmation + UX

Description: Display persisted chat history on load.
Steps:

On component mount call GET /api/history (gateway -> MCP -> Supabase) or call backend that queries Supabase directly.

Render messages ordered by created_at.

Show spinner while waiting.
Acceptance criteria: Previously stored messages appear correctly.

Sprint 6 — Testing, security hardening & CI
Story 6.1 — Unit & integration tests

Description: Add tests for verify middleware, MCP tools, and ai orchestration.
Steps:

Node: Jest tests for verify middleware with mocked Firebase admin.

Python: PyTest for supabase_client, ai_client with mocked Gemini responses (use VCR/pytest-mock).

Integration: Use FastAPI TestClient to call /mcp/query with test payloads.
Acceptance criteria: Tests pass locally and in CI.

Story 6.2 — Logging, monitoring, and rate limiting

Description: Add structured logging and basic rate limit for chat endpoint to prevent abuse.
Steps:

Integrate Winston (Node) / logging (Python).

Add middleware to limit requests per minute per UID (in Node gateway).

Track metrics (requests, errors) to stdout for platform metrics.
Acceptance criteria: Logs include request ID, user_id and status; rate limiting enforced.

Story 6.3 — Secret rotation and secure keys

Description: Ensure GEMINI keys and Supabase service role are only used server-side and rotated if leaked.
Steps:

Move keys to platform secret manager.

Revoke old keys if compromised.
Acceptance criteria: No keys checked into repo.

Sprint 7 — Advanced features & polish
Story 7.1 — Streaming responses (optional)

Description: Implement streaming from MCP -> gateway -> frontend for faster UX.
Steps:

Gemini SDK or HTTP streaming (if supported) to yield partial tokens.

Python side streams over SSE / WebSocket to Node gateway, or Node proxies streaming directly.

Frontend listens and appends tokens to message bubble.
Acceptance criteria: Frontend shows partial response while Gemini generates.

Story 7.2 — Embeddings & semantic search (memory)

Description: Compute embeddings for messages and store in Supabase vector column (or pgvector) to enable semantic memory retrieval.
Steps:

Add embeddings table or vector column.

After storing message, compute embedding via Gemini (or other embedding model) and store vector.

Implement get_relevant_context(query, top_k) tool to perform vector search.
Acceptance criteria: get_relevant_context returns relevant historical messages.

Story 7.3 — Tool calling & function execution

Description: Extend MCP toolset so Gemini can trigger actions (e.g., create a support ticket).
Steps:

Design tool signature with safe inputs/outputs.

Allow ai_client to choose to call tool, then re-query model with tool output.

Add safety checks and authorization vetting.
Acceptance criteria: Tools can be invoked and side effects are logged and reversible.

Deployment stories
Story D.1 — Dockerize MCP & Node services

Description: Add Dockerfiles and compose for local integration and production.
Steps:

Create Dockerfile for Node and Python services.

Create docker-compose.yaml for dev testing (local supabase or mimic).
Acceptance criteria: Services run locally with Docker Compose.

Story D.2 — Deploy to production

Description: Deploy Node backend to Render/Vercel and MCP server to Cloud Run or Fly.io; set env vars.
Steps:

Push images or use platform git integration.

Add environment variables on platform.

Test E2E over HTTPS.
Acceptance criteria: Production endpoint serves authenticated chat; logs show stable traffic.

Non-functional / cross-cutting stories
Story N.1 — Privacy & Compliance

Description: Document how PII is stored (email, uid) and retention policy. Provide user opt-out deletion endpoint.
Acceptance criteria: Privacy doc present and delete endpoint implemented.

Story N.2 — Cost & quota awareness

Description: Add usage logging to monitor Gemini API calls per user & total cost.
Acceptance criteria: Dashboard or CSV of usage available.

Acceptance matrix — end-to-end

When the following are true, we can call the project functionally complete:

Authenticated user can open the chat UI and send a message.

Node gateway verifies Firebase JWT.

Message forwarded to MCP server; MCP fetches user and last N messages from Supabase.

Gemini 2.5 Pro generates a context-aware reply.

Both user message and assistant reply are stored in Supabase.

Frontend displays reply and persisted history loads on page refresh.

Tests for middleware, MCP tools, and integration exist and pass.

Quick developer checklists

Before coding:

 .env.example created

 Supabase schema created

 Firebase service account accessible

Local dev:

 Run Supabase locally or use project

 Start Node backend npm run dev

 Start MCP uvicorn main:app --reload

 Login in frontend and test chat

To ship:

 Move env secrets to platform

 Add monitoring & error reporting

 Run security audit

Useful sample payloads & endpoints (for implementors)

Frontend → Node:

POST /api/chat
Headers: Authorization: Bearer <firebase_id_token>
Body: { "message": "Hi, show my last messages", "metadata": {} }


Node → MCP:

POST /mcp/query
Body:
{
  "user_id": "<firebaseUid>",
  "message": "Hi, show my last messages",
  "context": { "client": "web" }
}


MCP response:

{
  "reply": "Here are your last 3 messages: ...",
  "tools_called": ["get_chat_history"],
  "stored": true
}


Supabase SQL to fetch history (example):

select role, content, created_at
from messages
where user_id = (select id from users where firebase_uid = '<uid>')
order by created_at desc
limit 10;

Final notes & guardrails

Security: Because authentication uses Firebase, always verify tokens server-side — avoid trusting client-provided UIDs.

Supabase access: Use service role key server-side only. Do not expose it to clients.

Gemini keys: Keep GEMINI_API_KEY in server environments only (mcp_server).

RLS: If you later migrate to Supabase Auth, rework RLS policies to use auth.uid().

Iterate: Start minimal (store + reply) and add features (streaming, embeddings, function-calling) incrementally.