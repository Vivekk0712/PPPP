# Firebase Auth App — Phone, Google & Email/Password with AI Chat

A full-stack authentication system with AI-powered chat functionality. Built with React (frontend), Node.js + Express (backend), Python FastAPI (MCP server), Firebase Authentication, and Supabase database. Supports Phone OTP, Google Sign-In, and Email/Password with account linking, plus a ChatGPT-style AI assistant.

## Features

- Phone OTP (with Firebase reCAPTCHA)
- Google Sign-In
- Email/Password login
- Account linking (phone + Google + email)
- Secure session cookies (HttpOnly, Secure, SameSite=Strict)
- Firestore rules enforce per-user isolation
- **AI Chat Assistant** powered by Gemini 2.5 Pro
- **ChatGPT-style conversation management** with sidebar
- **Conversation isolation** - each chat maintains separate context
- **User-aware AI** - AI knows your name and profile information
- Ready for Firebase Emulator Suite

## Prerequisites

- Node.js >= 18
- Python 3.10+ and pip
- A Firebase project (the free tier is sufficient)
- A Supabase account (for database)
- Firebase CLI (`npm install -g firebase-tools`)
- Gemini API key (for AI functionality)

## Getting Started

Follow these steps to get the project up and running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/my-auth-app.git
cd my-auth-app
```

### 2. Install Dependencies

```bash
# Backend
cd backend && npm install

# Frontend
cd ../frontend && npm install

# MCP Server (Python)
cd ../mcp_server
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Firebase Project Setup

#### a. Create a Firebase Project
1.  Go to the [Firebase Console](https://console.firebase.google.com/).
2.  Click on "Add project" and follow the steps to create a new project.

#### b. Enable Authentication Providers
1.  In your new project, go to the **Authentication** section (from the left-hand menu).
2.  Click on the "Sign-in method" tab.
3.  Enable the following providers:
    *   **Email/Password**
    *   **Google**
    *   **Phone**

#### c. Get Frontend Configuration
1.  Go to your **Project Settings** (click the gear icon next to "Project Overview").
2.  In the "General" tab, scroll down to "Your apps".
3.  Click on the **Web** icon (`</>`) to create a new web app.
4.  Give it a nickname and register the app.
5.  Firebase will give you a `firebaseConfig` object. You will need these values for your `frontend/.env` file.

#### d. Get Backend Configuration (Service Account)
1.  In your **Project Settings**, go to the "Service accounts" tab.
2.  Click on "Generate new private key". This will download a JSON file.
3.  Rename this file to `serviceAccount.json` and place it in the `backend` directory.

#### e. Get reCAPTCHA Key for Phone Auth
1.  Phone authentication uses reCAPTCHA to prevent abuse.
2.  Go to the [Google Cloud Console](https://console.cloud.google.com/security/recaptcha) and set up a new reCAPTCHA v3 key.
3.  You will get a "Site Key". This is the value for `VITE_RECAPTCHA_SITE_KEY` in your `frontend/.env` file.

#### f. Set up Firestore
1.  In the Firebase Console, go to the **Firestore Database** section.
2.  Click "Create database" and start in **test mode**.

### 4. Supabase Database Setup

#### a. Create a Supabase Project
1. Go to the [Supabase Dashboard](https://app.supabase.io/) and create a new project.
2. Once the project is created, navigate to the **Project Settings** > **API** section.
3. You will need two pieces of information from this page for your `.env` files:
   - **Project URL** (looks like `https://<your-project-ref>.supabase.co`)
   - **Service Role Key** (under "Project API keys"). This key bypasses Row Level Security and should be kept secret.

#### b. Create Database Schema
1. In your Supabase project, go to the **SQL Editor**.
2. Click on **New query**.
3. Copy the entire content of the `mcp_server/db/schema.sql` file and paste it into the SQL editor.
4. Click **Run** to execute the script. This will create the `users`, `conversations`, `messages`, and `embeddings` tables.

### 5. Gemini API Setup
1. Go to the [Google AI Studio](https://aistudio.google.com/) to get your Gemini API key.
2. Create a new API key and copy it - you'll need this for the MCP server configuration.

### 6. Configure Environment Variables

Create a `.env` file in the `frontend`, `backend`, and `mcp_server` directories.

**`frontend/.env`**
```
VITE_API_BASE_URL=http://localhost:4000
VITE_FIREBASE_API_KEY=your-api-key-from-step-3c
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_APP_ID=your-app-id
VITE_RECAPTCHA_SITE_KEY=your-recaptcha-site-key-from-step-3e
```

**`backend/.env`**
```
PORT=4000
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./serviceAccount.json
SESSION_COOKIE_NAME=__session
SESSION_EXPIRES_IN=432000000   # 5 days in ms
MCP_SERVER_URL=http://localhost:8000
NODE_ENV=development
```

**`mcp_server/.env`**
```
SUPABASE_URL=your-supabase-project-url
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
GEMINI_API_KEY=your-gemini-api-key
NODE_ENV=development
```

### 7. Deploy Firestore Rules

To deploy the security rules for Firestore, run the following command from the root of the project:

```bash
firebase deploy --only firestore:rules
```

## Running the Application

You need to run all three services simultaneously in separate terminals.

### Start the Backend
```bash
cd backend
npm run dev
```
The backend server will start on `http://localhost:4000`.

### Start the MCP Server
```bash
cd mcp_server
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
uvicorn main:app --reload
```
The MCP server will start on `http://localhost:8000`.

### Start the Frontend
```bash
cd frontend
npm run dev
```
The frontend development server will start, usually on `http://localhost:5173`.

### Run with Firebase Emulator
To develop locally without connecting to your live Firebase project, you can use the Firebase Emulator Suite.

```bash
firebase emulators:start --only auth,firestore
```

## Repository Structure

```
/my-auth-app
  /backend
    /src
      /routes
      /middleware
      /services
  /frontend
    /src
      /components
      /pages
      /services
  /mcp_server
    /tools
    /db
  /docs
  README.md
  firebase.json
  firebase.rules
```

## Testing

- **Unit tests:** Jest + Supertest (backend), React Testing Library (frontend)
- **E2E:** Playwright or Cypress with Firebase Emulator

## Security

- Session cookies are HttpOnly, Secure, SameSite=Strict
- reCAPTCHA required for phone OTP
- Strong password policy for email/password
- Firestore rules prevent cross-user access

## AI Chat Features

- **Gemini 2.5 Pro Integration**: Powered by Google's latest AI model
- **Conversation Management**: ChatGPT-style sidebar with conversation history
- **Context Isolation**: Each conversation maintains separate context
- **User Awareness**: AI knows your name and profile information
- **Message History**: Persistent chat history stored in Supabase
- **Real-time Chat**: Instant responses with loading indicators
- **Fullscreen Mode**: Immersive chat experience
- **Conversation CRUD**: Create, switch, and delete conversations

## Roadmap

- Password reset & email verification
- Roles (admin/user)
- Multi-factor auth (MFA)
- AI conversation search and filtering
- Message export functionality
- Deployment (Netlify + Render/Cloud Run)

## License

MIT
