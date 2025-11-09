# MCP Server & Supabase Setup Guide

This guide provides instructions on how to set up the Python-based MCP server, configure the Supabase database, and run the full application stack locally.

## 1. Prerequisites

- **Node.js and npm:** Required for the `frontend` and `backend` services.
- **Python 3.10+ and pip:** Required for the `mcp_server`.
- **Firebase Project:** A pre-existing Firebase project is required for authentication.
- **Supabase Account:** A Supabase account is needed for the database.

## 2. Supabase Setup

### a. Create a Supabase Project
1. Go to the [Supabase Dashboard](https://app.supabase.io/) and create a new project.
2. Once the project is created, navigate to the **Project Settings** > **API** section.
3. You will need two pieces of information from this page for your `.env` files:
   - **Project URL** (looks like `https://<your-project-ref>.supabase.co`)
   - **Service Role Key** (under "Project API keys"). This key bypasses Row Level Security and should be kept secret.

### b. Create Database Schema
1. In your Supabase project, go to the **SQL Editor**.
2. Click on **New query**.
3. Copy the entire content of the `mcp_server/db/schema.sql` file and paste it into the SQL editor.
4. Click **Run** to execute the script. This will create the `users`, `messages`, and `embeddings` tables.

## 3. Environment Setup

You will need to create `.env` files for both the `backend` and `mcp_server`.

### a. Backend (`backend/.env`)
Create a `.env` file in the `backend` directory and add the following variables. Use `backend/.env.example` as a template.

```env
# Firebase Project ID
FIREBASE_PROJECT_ID="your-firebase-project-id"

# Port for the backend server
PORT=4000

# Session cookie configuration
SESSION_COOKIE_NAME="your-session-cookie-name"
SESSION_EXPIRES_IN="1209600000" # 14 days in milliseconds

# URL of the MCP server
MCP_SERVER_URL="http://localhost:8000"
```

You also need to set up **Firebase Admin SDK credentials**. The current setup uses Application Default Credentials. Refer to the Firebase documentation for instructions on how to set this up for your environment.

### b. MCP Server (`mcp_server/.env`)
Create a `.env` file in the `mcp_server` directory and add the following variables. Use `mcp_server/.env.example` as a template.

```env
# Supabase Credentials
SUPABASE_URL="your-supabase-project-url"
SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"

# Gemini API Key
GEMINI_API_KEY="your-gemini-api-key"

# Environment (development or production)
NODE_ENV=development
```

## 4. Installation

### a. Backend
```bash
cd backend
npm install
```

### b. Frontend
```bash
cd frontend
npm install
```

### c. MCP Server
It is recommended to use a virtual environment for the Python dependencies.
```bash
cd mcp_server
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

## 5. Running the Application

You will need to run all three services simultaneously in separate terminals.

### a. Start the Backend
```bash
cd backend
npm run dev
```
The backend server will start on `http://localhost:4000`.

### b. Start the MCP Server
```bash
cd mcp_server
source venv/bin/activate  # If not already activated
uvicorn main:app --reload
```
The MCP server will start on `http://localhost:8000`.

### c. Start the Frontend
```bash
cd frontend
npm run dev
```
The frontend development server will start, usually on `http://localhost:5173`. You can access the application in your browser at this address.
