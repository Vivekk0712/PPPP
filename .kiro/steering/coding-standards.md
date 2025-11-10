---
inclusion: always
---

# Coding Standards for AutoML Platform

## Python Code Standards

### Imports
- Use absolute imports
- Group imports: standard library, third-party, local
- Use type hints for function parameters and returns

### Error Handling
- Always log errors to both console and `agent_logs` table
- Use try-except blocks for external API calls
- Include traceback for debugging

### Database Operations
- Always convert Firebase UID to User UUID before queries
- Use UTC timestamps (avoid deprecated `datetime.utcnow()`)
- Log all database operations

### Agent Development
- Each agent runs on its own port (8001, 8002, 8003, 8004)
- Use FastAPI for all agent services
- Include health check endpoint
- Log all activities to Supabase `agent_logs` table

## JavaScript/React Standards

### Components
- Use functional components with hooks
- Use Framer Motion for animations
- Keep components under 300 lines
- Extract reusable logic into custom hooks

### API Calls
- Use axios with proper error handling
- Show loading states during async operations
- Display user-friendly error messages
- Use try-catch blocks

### Styling
- Use Bootstrap for layout
- Use inline styles for custom styling
- Maintain consistent color scheme (gradients)
- Ensure responsive design (mobile-first)

## Environment Variables

### Required for Each Service

**Frontend (.env):**
- VITE_API_BASE_URL
- VITE_FIREBASE_* (all Firebase config)

**Backend (.env):**
- PORT
- MCP_SERVER_URL
- FIREBASE_PROJECT_ID
- GOOGLE_APPLICATION_CREDENTIALS

**MCP Server (.env):**
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY
- GEMINI_API_KEY
- PLANNER_AGENT_URL
- DATASET_AGENT_URL

**Agents (.env):**
- SUPABASE_URL
- SUPABASE_KEY
- GEMINI_API_KEY (Planner)
- GCP_BUCKET_NAME (Dataset)
- KAGGLE_USERNAME (Dataset)
- KAGGLE_KEY (Dataset)

## Git Practices

### Commit Messages
- Use conventional commits format
- Examples: `feat:`, `fix:`, `docs:`, `refactor:`

### Branches
- `main` - Production ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches

## Testing

- Test each agent independently before integration
- Use health check endpoints to verify services
- Check database after each operation
- Monitor agent logs for errors
