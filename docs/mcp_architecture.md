1. Background

This project is an AI-augmented authentication platform designed to provide personalized and intelligent user experiences after login.
It extends a pre-existing Firebase + Node.js authentication system by integrating:

a Python-based Model Context Protocol (MCP) Server,

Gemini 2.5 Pro as the core reasoning engine, and

Supabase for structured data storage and contextual grounding.

After user authentication, a Gemini-powered chatbot is available to each logged-in user, capable of retrieving user data, responding contextually, and performing tool-based actions through the MCP interface.

2. Motivation

The motivation behind this architecture is to create a modular, intelligent backend where:

Gemini LLM can access real-time, structured, and authenticated data from Supabase.

The application remains secure, scalable, and LLM-agnostic through the MCP standard.

Developers can define “tools” (functions) in Python that Gemini can call dynamically to query, analyze, or update data.

This design aligns with LLM system interoperability, allowing future integration with other models or agents (e.g., Claude, GPT-5, etc.) without changing the overall data flow.

3. System Overview
Core Components
Component	Description
React Frontend	Handles user UI, login flow, and chatbot interface.
Firebase Auth	Provides secure user authentication via Email, Google, or Phone.
Node.js Backend	Acts as an authentication and communication gateway between the frontend and Python MCP server.
Python MCP Server	Defines “tools” and integrates Gemini 2.5 Pro for reasoning.
Supabase	PostgreSQL-based database that stores user data, message history, and context.
Gemini 2.5 Pro LLM	The intelligence core handling language understanding, context retrieval, and reasoning.
4. System Architecture
+---------------------------+
|        React Frontend     |
|  - Login (Firebase Auth)  |
|  - Chatbot UI             |
+-------------+-------------+
              |
              v
+-------------+-------------+
|     Node.js Backend       |
| - Verifies Firebase Token |
| - API Gateway to MCP      |
| - Caches Session Context  |
+-------------+-------------+
              |
              v
+-------------+-------------+
|   Python MCP Server       |
| - Gemini 2.5 Pro client   |
| - Supabase connector      |
| - Defined MCP tools:      |
|   • get_user_profile()    |
|   • get_chat_history()    |
|   • store_message()       |
|   • contextual_reasoning()|
+-------------+-------------+
              |
              v
+-------------+-------------+
|       Supabase DB         |
|  - users table            |
|  - messages table         |
|  - preferences table      |
+---------------------------+

Gemini 2.5 Pro <----> MCP Server (via SDK)

5. Data Flow

1️⃣ Login & Token Verification

The user logs in via Firebase on the frontend.

The ID token is sent to the Node.js backend with each API request.

The backend verifies the token using Firebase Admin SDK.

2️⃣ Chat Request

Frontend sends user input to /api/chat.

Backend forwards it (with verified UID) to the Python MCP server.

3️⃣ MCP Processing

MCP Server initializes Gemini 2.5 Pro.

The input is wrapped with contextual metadata (user ID, last N messages, preferences).

Gemini reasons using available tools:

Fetch user profile from Supabase.

Retrieve prior chat context.

Store response after generation.

4️⃣ Response Delivery

MCP Server returns Gemini’s structured response to Node.js backend.

Backend forwards it to the React frontend.

Chatbot displays the AI reply.

6. MCP Tool Design

Example tools exposed by the MCP server:

Tool Name	Purpose	Connected System
get_user_profile(uid)	Retrieve authenticated user profile details.	Supabase
get_chat_history(uid, limit=10)	Retrieve recent chat messages for context.	Supabase
store_message(uid, message, role)	Store user or AI message.	Supabase
contextual_reasoning(input)	Pass structured input to Gemini 2.5 Pro.	Gemini API

These tools follow the Model Context Protocol (MCP) standard so Gemini can automatically decide when to call them.

7. Database Schema (Supabase)
Table: users
Column	Type	Description
id	UUID	User ID (matches Firebase UID)
name	TEXT	Display name
email	TEXT	Email address
created_at	TIMESTAMP	Timestamp of creation
Table: messages
Column	Type	Description
id	UUID	Message ID
user_id	UUID	Foreign key to users
role	TEXT	Either "user" or "assistant"
content	TEXT	Message text
timestamp	TIMESTAMP	Message creation time
8. Security Model

Authentication:
Firebase handles user identity.
Node.js backend validates the Firebase ID token before forwarding requests.

Authorization:
Only verified users’ UIDs are allowed to interact with the MCP server.

Data Access:
Supabase Row-Level Security (RLS) ensures that users can only access their own data.

Secret Management:

Gemini API key and Supabase keys stored in environment variables.

.env file never committed to version control.

9. Tech Stack Summary
Layer	Technology
Frontend	React + Framer Motion + Bootstrap
Auth	Firebase Auth
Backend Gateway	Node.js (Express)
MCP Server	Python (FastAPI + MCP SDK)
Database	Supabase (PostgreSQL)
AI Model	Gemini 2.5 Pro
Protocol	Model Context Protocol (MCP)
Deployment	Vercel (Frontend + Node), Railway/Fly.io (MCP), Supabase Cloud
10. Future Enhancements

🔹 Add user-specific memory with vector embeddings in Supabase.

🔹 Enable function-calling via Gemini to dynamically execute MCP tools.

🔹 Add analytics dashboard showing AI usage per user.

🔹 Enable streaming responses from Gemini for real-time chatbot UX.

🔹 Multi-modal expansion (image + text input) with Gemini 2.5 Pro.

11. Summary

This architecture provides a secure, modular, and scalable AI system where:

Firebase handles identity.

Node.js maintains control and communication.

Python MCP server orchestrates Gemini reasoning and Supabase integration.

Supabase provides structured data context.

Together, these components form an intelligent, connected ecosystem capable of contextual AI reasoning across authenticated users — a foundational step toward a fully personalized AI assistant platform.