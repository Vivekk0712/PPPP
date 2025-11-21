# AutoML Platform — Multi-Agent Machine Learning Pipeline

A full-stack AutoML platform with multi-agent orchestration for automated machine learning workflows. Built with React (frontend), Node.js + Express (backend), Python FastAPI (MCP server + AI agents), Firebase Authentication, and Supabase database. Features intelligent project planning, automated dataset acquisition, model training, evaluation, and testing capabilities.

## 🚀 Features

### Authentication & Security
- Phone OTP (with Firebase reCAPTCHA)
- Google Sign-In
- Email/Password login
- Account linking (phone + Google + email)
- Secure session cookies (HttpOnly, Secure, SameSite=Strict)
- Firebase UID → User UUID conversion for database operations

### AutoML Pipeline
- **Intelligent Project Planning** - AI-powered intent parsing and project structuring
- **Automated Dataset Acquisition** - Kaggle integration with smart search and download
- **Model Training** - PyTorch-based training with GPU/CPU support
- **Model Evaluation** - Comprehensive metrics and performance analysis
- **Model Testing** - Upload images and test trained models in real-time

### AI Agents (Multi-Agent Architecture)
1. **Planner Agent (Port 8001)** - Gemini-powered project planning and intent extraction
2. **Dataset Agent (Port 8002)** - Auto-polling Kaggle dataset search and GCP upload
3. **Training Agent (Port 8003)** - PyTorch model training with progress tracking
4. **Evaluation Agent (Port 8004)** - Model evaluation and metrics generation

### User Interface
- **ML Projects Dashboard** - Visual project cards with status tracking
- **ChatGPT-style ML Chat** - Natural language ML project creation
- **Agent Logs Viewer** - Real-time agent activity monitoring
- **Model Testing Interface** - Upload and test images with trained models
- **Admin Dashboard** - System-wide monitoring and management
- **Auto-refresh** - Real-time project status updates

### Advanced Features
- **Dataset Size Limits** - Specify size constraints in natural language (e.g., "not more than 1GB")
- **Auto-polling** - Dataset Agent automatically processes pending projects every 10 seconds
- **Progress Tracking** - Visual progress indicators (25%, 50%, 75%, 100%)
- **Agent Logging** - All agent activities logged to database
- **GCP Integration** - Cloud storage for datasets and models
- **Kaggle API** - Automated dataset search and download

## 📋 Prerequisites

- Node.js >= 18
- Python 3.10+ and pip
- A Firebase project (the free tier is sufficient)
- A Supabase account (for database)
- Firebase CLI (`npm install -g firebase-tools`)
- Gemini API key (for AI functionality)
- Google Cloud Platform account (for dataset/model storage)
- Kaggle API credentials (for dataset acquisition)
- PyTorch (CPU or GPU version depending on your hardware)

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
cd backend
npm install

# Frontend
cd frontend
npm install

# MCP Server (Python)
cd mcp_server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Planner Agent
cd Planner-Agent/agent/planner
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Dataset Agent
cd Dataset_Agent/agents/dataset
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Training Agent
cd Trainer-Agent/agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# For CPU: pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
# For GPU: See Trainer-Agent/agent/for_NVIDIA_GPU.txt
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
3. Copy the entire content of the `schema.sql` file and paste it into the SQL editor.
4. Click **Run** to execute the script. This will create all required tables:
   - `users` - User profiles with Firebase UID mapping
   - `conversations` - Chat conversation history
   - `messages` - Individual chat messages
   - `projects` - ML project metadata and status
   - `datasets` - Dataset information and GCP URLs
   - `models` - Trained model information
   - `agent_logs` - Agent execution logs and activities

### 5. Gemini API Setup
1. Go to the [Google AI Studio](https://aistudio.google.com/) to get your Gemini API key.
2. Create a new API key and copy it - you'll need this for the MCP server and Planner Agent.

### 6. Google Cloud Platform Setup
1. Create a GCP project and enable Cloud Storage API
2. Create a storage bucket for datasets and models
3. Download service account credentials JSON file
4. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the JSON file path

### 7. Kaggle API Setup
1. Go to [Kaggle Account Settings](https://www.kaggle.com/settings)
2. Click "Create New API Token" to download `kaggle.json`
3. Extract username and key from the JSON file
4. Add these credentials to Dataset Agent `.env` file

### 8. Configure Environment Variables

Create `.env` files in each service directory:

**`frontend/.env`**
```env
VITE_API_BASE_URL=http://localhost:4000
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_APP_ID=your-app-id
VITE_RECAPTCHA_SITE_KEY=your-recaptcha-site-key
```

**`backend/.env`**
```env
PORT=4000
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./serviceAccount.json
SESSION_COOKIE_NAME=__session
SESSION_EXPIRES_IN=432000000
MCP_SERVER_URL=http://localhost:8000
NODE_ENV=development
```

**`mcp_server/.env`**
```env
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-supabase-key
GEMINI_API_KEY=your-gemini-api-key
PLANNER_AGENT_URL=http://localhost:8001
DATASET_AGENT_URL=http://localhost:8002
TRAINING_AGENT_URL=http://localhost:8003
EVALUATION_AGENT_URL=http://localhost:8004
NODE_ENV=development
```

**`Planner-Agent/agent/planner/.env`**
```env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
GEMINI_API_KEY=your-gemini-api-key
PORT=8001
```

**`Dataset_Agent/agents/dataset/.env`**
```env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-key
GCP_BUCKET_NAME=your-gcp-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/gcp-credentials.json
PORT=8002
```

**`Trainer-Agent/agent/.env`**
```env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
GCP_BUCKET_NAME=your-gcp-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/gcp-credentials.json
PORT=8003
```

### 9. Deploy Firestore Rules

```bash
firebase deploy --only firestore:rules
```

## 🏃 Running the Application

You need to run all services simultaneously. Open separate terminals for each:

### Terminal 1: Backend (Node.js)
```bash
cd backend
npm run dev
```
Server starts on `http://localhost:4000`

### Terminal 2: Frontend (React)
```bash
cd frontend
npm run dev
```
Server starts on `http://localhost:5173`

### Terminal 3: MCP Server (Python)
```bash
cd mcp_server
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload
```
Server starts on `http://localhost:8000`

### Terminal 4: Planner Agent
```bash
cd Planner-Agent/agent/planner
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload --port 8001
```
Server starts on `http://localhost:8001`

### Terminal 5: Dataset Agent
```bash
cd Dataset_Agent/agents/dataset
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```
Server starts on `http://localhost:8002` with auto-polling enabled

### Terminal 6: Training Agent
```bash
cd Trainer-Agent/agent
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```
Server starts on `http://localhost:8003` with auto-polling enabled

### Quick Start Scripts (Windows)
```bash
# Start all agents at once
start-training-agent.bat
```

### Run with Firebase Emulator
To develop locally without connecting to your live Firebase project, you can use the Firebase Emulator Suite.

```bash
firebase emulators:start --only auth,firestore
```

## 📁 Repository Structure

```
/automl-platform
  /backend                          # Node.js + Express backend
    /src
      /routes                       # API routes (auth, ml, chat)
      /middleware                   # Authentication middleware
      /services                     # Business logic
    serviceAccount.json             # Firebase admin credentials
    
  /frontend                         # React + Vite frontend
    /src
      /components                   # Reusable components
        ChatBot.jsx                 # General AI chat
        MLChatBot.jsx               # ML project chat
        ModelTester.jsx             # Model testing interface
        AgentLogsViewer.jsx         # Agent activity logs
        ProjectCard.jsx             # Project display card
        ProjectList.jsx             # Project grid view
      /pages
        Dashboard.jsx               # Main dashboard
        MLProjectsPage.jsx          # ML projects page
        AdminDashboard.jsx          # Admin panel
      /services
        mlApi.js                    # ML API client
        
  /mcp_server                       # Python FastAPI orchestrator
    main.py                         # MCP server entry point
    requirements.txt                # Python dependencies
    
  /Planner-Agent                    # AI project planning agent
    /agent/planner
      main.py                       # Planner agent server
      requirements.txt              # Dependencies
      
  /Dataset_Agent                    # Kaggle dataset agent
    /agents/dataset
      main.py                       # Dataset agent with auto-polling
      requirements.txt              # Dependencies
      
  /Trainer-Agent                    # PyTorch training agent
    /agent
      main.py                       # Training agent with auto-polling
      /services
        training_service.py         # Training logic
        evaluation_service.py       # Evaluation logic
      requirements.txt              # Dependencies
      for_NVIDIA_GPU.txt            # GPU setup instructions
      
  schema.sql                        # Complete database schema
  firebase.json                     # Firebase configuration
  firebase.rules                    # Firestore security rules
  
  # Documentation
  QUICK_START.md                    # Quick start guide
  SETUP_GUIDE.md                    # Detailed setup
  TESTING_GUIDE.md                  # Testing instructions
  FEATURES_OVERVIEW.md              # Feature documentation
  IMPLEMENTATION_SUMMARY.md         # Implementation details
```

## Testing

- **Unit tests:** Jest + Supertest (backend), React Testing Library (frontend)
- **E2E:** Playwright or Cypress with Firebase Emulator

## Security

- Session cookies are HttpOnly, Secure, SameSite=Strict
- reCAPTCHA required for phone OTP
- Strong password policy for email/password
- Firestore rules prevent cross-user access

## 🎯 How It Works

### 1. Project Creation Flow
```
User Chat → Planner Agent → Project Created (pending_dataset)
```
- User describes ML project in natural language
- Planner Agent extracts intent, problem type, dataset requirements
- Creates project with status `pending_dataset`
- Supports dataset size limits (e.g., "not more than 1GB")

### 2. Dataset Acquisition Flow
```
Auto-polling → Kaggle Search → Download → GCP Upload → Status Update
```
- Dataset Agent polls every 10 seconds for `pending_dataset` projects
- Searches Kaggle with intelligent query generation
- Downloads dataset respecting size limits
- Uploads to GCP bucket
- Updates project status to `pending_training`

### 3. Training Flow
```
Auto-polling → Download Dataset → Train Model → Upload Model → Status Update
```
- Training Agent polls for `pending_training` projects
- Downloads dataset from GCP
- Trains PyTorch model (ResNet18 for images, custom for others)
- Uploads trained model to GCP
- Updates project status to `pending_evaluation`

### 4. Evaluation Flow
```
Auto-polling → Download Model → Evaluate → Generate Metrics → Complete
```
- Evaluation Agent polls for `pending_evaluation` projects
- Downloads model and test data
- Generates comprehensive metrics
- Updates project status to `completed`

### 5. Model Testing
```
Upload Image → Download Model → Run Inference → Display Results
```
- User uploads image in Model Tester
- Backend downloads model from GCP
- Runs inference with PyTorch
- Returns prediction and confidence score

## 🎨 User Interface Features

### ML Projects Dashboard
- Visual project cards with gradient backgrounds
- Real-time status indicators (25%, 50%, 75%, 100%)
- Auto-refresh every 5 seconds
- Filter and search capabilities
- Responsive grid layout

### ML Chat Interface
- ChatGPT-style conversation UI
- Natural language project creation
- Real-time agent activity updates
- Message history persistence
- Fullscreen mode

### Agent Logs Viewer
- Real-time agent activity monitoring
- Color-coded log levels (info, success, error)
- Filterable by agent type
- Timestamp tracking
- Auto-scroll to latest logs

### Model Testing Interface
- Drag-and-drop image upload
- Real-time inference results
- Confidence score visualization
- Support for all trained models
- Error handling and validation

### Admin Dashboard
- System-wide statistics
- User management
- Project monitoring
- Agent health checks
- Database metrics

## 🧪 Testing

### Manual Testing
```bash
# Test Planner Agent
python test-planner.py

# Test Dataset Agent
python test-dataset-agent.py

# Test complete flow
python test-dataset-flow.py

# Check database status
python check-database-status.py

# Check models
python check-models.py

# Fix stuck projects
python fix-stuck-projects.py
```

### Health Checks
```bash
# Backend
curl http://localhost:4000/health

# MCP Server
curl http://localhost:8000/health

# Planner Agent
curl http://localhost:8001/health

# Dataset Agent
curl http://localhost:8002/health

# Training Agent
curl http://localhost:8003/health
```

## 🔧 Troubleshooting

### Common Issues

**Dataset Agent not processing projects**
- Check Kaggle credentials in `.env`
- Verify GCP bucket permissions
- Check agent logs in database

**Training Agent fails**
- Ensure PyTorch is installed correctly
- Check GPU/CPU compatibility
- Verify dataset format in GCP

**Model testing not working**
- Install `multer` in backend: `npm install multer`
- Install PyTorch in MCP server
- Check model file exists in GCP

**Projects stuck in pending status**
- Run `python fix-stuck-projects.py`
- Check agent logs for errors
- Verify all agents are running

### Windows-Specific Issues
- Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- Use `&` instead of `&&` in CMD commands
- Check `start-training-agent.bat` for batch script examples

## 🚀 Deployment

### Frontend (Netlify/Vercel)
```bash
cd frontend
npm run build
# Deploy dist/ folder
```

### Backend (Render/Railway)
```bash
cd backend
# Set environment variables
# Deploy with Node.js 18+
```

### Python Services (Google Cloud Run)
```bash
# Build Docker images for each agent
docker build -t planner-agent ./Planner-Agent/agent/planner
docker build -t dataset-agent ./Dataset_Agent/agents/dataset
docker build -t training-agent ./Trainer-Agent/agent

# Push to container registry
# Deploy to Cloud Run
```

## 📊 Database Schema

### Core Tables
- **users** - User profiles with Firebase UID mapping
- **projects** - ML project metadata and status tracking
- **datasets** - Dataset information and GCP URLs
- **models** - Trained model metadata
- **agent_logs** - Agent execution logs

### Status Flow
```
pending_dataset → pending_training → pending_evaluation → completed
```

## 🔐 Security

- Session cookies: HttpOnly, Secure, SameSite=Strict
- Firebase UID → UUID conversion for all database operations
- Row-level security in Supabase
- GCP service account authentication
- API key protection for Kaggle and Gemini
- Input validation and sanitization

## 📚 Documentation

- **QUICK_START.md** - Get started in 5 minutes
- **SETUP_GUIDE.md** - Detailed setup instructions
- **TESTING_GUIDE.md** - Testing procedures
- **FEATURES_OVERVIEW.md** - Complete feature list
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **DATASET_SIZE_LIMIT_FEATURE.md** - Size limit feature documentation
- **MODEL_TESTING_SETUP.md** - Model testing setup guide

## 🛣️ Roadmap

### Completed ✅
- Multi-agent architecture
- Automated dataset acquisition
- Model training pipeline
- Model evaluation
- Model testing interface
- Admin dashboard
- Agent logging system
- Auto-refresh UI
- Dataset size limits

### In Progress 🚧
- Advanced model architectures
- Hyperparameter tuning
- Model versioning
- Experiment tracking

### Planned 📋
- Multi-model comparison
- AutoML hyperparameter optimization
- Distributed training support
- Model deployment API
- Custom dataset upload
- Transfer learning support
- Model explainability tools
- Collaborative projects
- API rate limiting
- Cost estimation
- Email notifications

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the coding standards in `.kiro/steering/coding-standards.md`
4. Test your changes thoroughly
5. Commit with conventional commits (`feat:`, `fix:`, `docs:`)
6. Push to your branch
7. Open a Pull Request

## 📝 License

MIT

## 👥 Authors

Built with ❤️ for the AutoML community

## 🙏 Acknowledgments

- Google Gemini AI for intelligent planning
- Kaggle for dataset access
- PyTorch for model training
- Supabase for database
- Firebase for authentication
- Google Cloud Platform for storage

## 📞 Support

For issues and questions:
- Check the documentation in `/docs`
- Review troubleshooting section
- Check agent logs in database
- Open an issue on GitHub

---

**Happy AutoML-ing! 🚀🤖**
