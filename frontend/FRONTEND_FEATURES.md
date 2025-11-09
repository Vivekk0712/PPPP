# AutoML Platform - Frontend Features

## Overview
A beautiful, professional UI for creating and managing machine learning projects with AI-powered assistance.

## Features

### 1. **Home Dashboard**
- Welcome screen with quick access cards
- Navigation to ML Projects, Model Testing, and AI Chat
- Beautiful gradient designs and smooth animations
- Responsive layout for all screen sizes

### 2. **ML Projects Tab**
Create and manage your machine learning projects with an intuitive interface.

#### ML Chat Assistant
- Dedicated chatbot for creating ML projects
- Example prompts to get started quickly
- Real-time project creation
- Beautiful gradient purple theme

#### Project Cards
- Visual status indicators with progress bars
- Color-coded status badges (Draft, Training, Completed, etc.)
- Display accuracy metrics when available
- Quick actions: View Details, Download Model
- Keyword tags for easy identification

#### Project Details Modal
- Agent pipeline visualization showing progress through:
  - 🎯 Planner Agent
  - 📦 Dataset Agent
  - ⚙️ Training Agent
  - 📊 Evaluation Agent
- Animated progress indicators
- Detailed metadata view
- Download model button for completed projects

### 3. **Test Model Tab**
Upload images to test your trained models.

#### Features:
- Dropdown to select from completed models
- Drag-and-drop image upload
- Image preview before testing
- Real-time prediction results
- Confidence scores display
- Beautiful gradient orange theme

### 4. **General Chat Assistant**
Keep the existing chatbot for general conversations.

#### Features:
- Persistent chat history (localStorage)
- Fullscreen mode
- Clear chat history option
- Smooth animations
- Timestamp for each message

### 5. **Profile Management**
- Modal overlay for profile editing
- Update name and phone number
- User-specific data storage
- Clean, modern design

## Design System

### Color Palette
- **Primary Purple**: `#667eea` to `#764ba2` (ML Projects)
- **Orange**: `#f59e0b` to `#d97706` (Model Testing)
- **Green**: `#10b981` to `#059669` (Success states)
- **Blue**: `#3b82f6` to `#2563eb` (Active states)
- **Gray Scale**: Modern neutral tones

### Typography
- Clean, readable fonts
- Proper hierarchy with font weights
- Responsive sizing

### Components
- Rounded corners (12px-20px)
- Smooth shadows and gradients
- Hover effects and transitions
- Loading states with spinners
- Toast notifications for actions

### Animations
- Framer Motion for smooth transitions
- Staggered children animations
- Hover and tap feedback
- Page transitions

## API Integration

### ML Endpoints
```javascript
// Create ML project
POST /api/ml/chat
Body: { message: "Train a model for..." }

// Get all projects
GET /api/ml/projects

// Get project details
GET /api/ml/projects/:projectId

// Get project logs
GET /api/ml/projects/:projectId/logs

// Download model
GET /api/ml/projects/:projectId/download

// Test model
POST /api/ml/projects/:projectId/test
Body: FormData with image file
```

### Chat Endpoints (Existing)
```javascript
// Send message
POST /api/chat

// Get history
GET /api/history

// Clear chat
DELETE /api/clear-chat
```

## File Structure
```
frontend/src/
├── components/
│   ├── ChatBot.jsx              # General chat assistant
│   ├── MLChatBot.jsx            # ML project creation chat
│   ├── ProjectCard.jsx          # Individual project card
│   ├── ProjectList.jsx          # List of all projects
│   ├── ModelTester.jsx          # Image upload & testing
│   └── [auth components]        # Existing auth components
├── pages/
│   ├── Dashboard.jsx            # Main dashboard with tabs
│   ├── MLProjectsPage.jsx       # ML projects interface
│   └── LoginPage.jsx            # Existing login
├── services/
│   ├── api.js                   # General API calls
│   └── mlApi.js                 # ML-specific API calls
└── App.css                      # Global styles
```

## Responsive Design
- Mobile-first approach
- Breakpoints for tablets and desktops
- Touch-friendly interactions
- Optimized layouts for all screen sizes

## User Experience
- Intuitive navigation
- Clear visual feedback
- Loading states for async operations
- Error handling with user-friendly messages
- Smooth transitions between states
- Accessibility considerations

## Future Enhancements
- Real-time project status updates via WebSocket
- Model comparison dashboard
- Training metrics visualization (loss curves, etc.)
- Dataset preview before training
- Hyperparameter tuning interface
- Model versioning
- Collaborative features
- Export to different formats
