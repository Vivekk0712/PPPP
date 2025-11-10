# Admin Panel Feature

## Overview

Added a comprehensive admin dashboard to view and manage all system data including users, projects, datasets, models, and logs.

## Features

### 📊 Statistics Dashboard
- **Total Users** - Count of all registered users
- **Total Projects** - All ML projects across users
- **Total Datasets** - Downloaded datasets count
- **Trained Models** - Successfully trained models count
- **Recent Activity** - Projects created in last 24 hours
- **Status Breakdown** - Visual breakdown of project statuses

### 👥 Users Management
- View all registered users
- Firebase UID and email
- Project count per user
- Registration date

### 📁 Projects Overview
- All projects across all users
- Project name, status, framework
- User information
- Creation timestamps
- Status badges (completed, failed, pending, etc.)

### 📋 System Logs
- Recent agent logs (last 100)
- Agent name, log level, message
- Project association
- Timestamp
- Color-coded by severity (error, warning, info)

## Implementation

### Backend (MCP Server)

**New Endpoints** (`mcp_server/main.py`):
- `GET /api/admin/stats` - System statistics
- `GET /api/admin/users` - All users with project counts
- `GET /api/admin/projects` - All projects (limit: 50)
- `GET /api/admin/logs` - Recent logs (limit: 100)

**Authentication**: Simple admin key validation (`ADMIN_KEY` in .env)

### Backend (Node.js)

**New Routes** (`backend/src/routes/ml.js`):
- `GET /api/admin/stats` - Proxy to MCP server
- `GET /api/admin/users` - Proxy to MCP server
- `GET /api/admin/projects` - Proxy to MCP server
- `GET /api/admin/logs` - Proxy to MCP server

### Frontend

**New Files**:
- `frontend/src/services/adminApi.js` - Admin API service
- `frontend/src/pages/AdminDashboard.jsx` - Admin dashboard page

**Updated Files**:
- `frontend/src/pages/Dashboard.jsx` - Added admin tab

## Access

### Admin Tab
Located in the main dashboard navigation:
- Home
- ML Projects
- Test Model
- **Admin** ← New tab

### Security

**Role-Based Access Control**: Admin access is controlled by the `is_admin` column in the users table.

### Setting Up Admin Users

1. **Update user in Supabase**:
   ```sql
   UPDATE users 
   SET is_admin = true 
   WHERE firebase_uid = 'your_firebase_uid';
   ```

2. **Or via Supabase Dashboard**:
   - Go to Table Editor → users
   - Find your user
   - Set `is_admin` to `true`

### How It Works

1. User logs in with Firebase
2. Frontend checks admin status on mount
3. Admin tab only shows if user has `is_admin = true`
4. Backend validates admin status on every API call
5. MCP Server double-checks admin role from database

## Usage

1. **Login** to the application
2. **Click "Admin" tab** in the navigation
3. **View statistics** at the top (4 stat cards)
4. **Browse data** using tabs:
   - Users tab - All registered users
   - Projects tab - All ML projects
   - Logs tab - Recent agent activity

## Data Displayed

### Statistics Cards
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total Users │   Projects  │  Datasets   │   Models    │
│     👥      │     📁      │     💾      │     🤖      │
│     15      │     42      │     38      │     25      │
│             │  +5 today   │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Status Breakdown
Visual display of project statuses:
- Draft
- Pending Dataset
- Pending Training
- Pending Evaluation
- Completed
- Failed

### Users Table
| Firebase UID | Email | Projects | Created |
|--------------|-------|----------|---------|
| abc123... | user@example.com | 5 | 2025-11-10 |

### Projects Table
| Name | User | Status | Framework | Created |
|------|------|--------|-----------|---------|
| Flower Classifier | abc123... | completed | PyTorch | 2025-11-10 |

### Logs Table
| Time | Agent | Project | Level | Message |
|------|-------|---------|-------|---------|
| 10:30 | dataset | Flower... | info | Dataset uploaded |

## Styling

- **Modern UI** with gradient cards
- **Color-coded badges** for status and log levels
- **Responsive design** works on mobile and desktop
- **Smooth animations** using Framer Motion
- **Scrollable tables** for large datasets

## Security Considerations

### Production Deployment

1. **Change Admin Key**:
   ```bash
   # Use a strong, random key
   ADMIN_KEY=your_very_secure_random_key_here_min_32_chars
   ```

2. **Add Role-Based Access**:
   - Store admin role in database
   - Check user role before showing admin tab
   - Validate admin role on backend

3. **Add Audit Logging**:
   - Log all admin actions
   - Track who accessed what data
   - Monitor for suspicious activity

4. **Rate Limiting**:
   - Limit admin API calls
   - Prevent brute force attacks
   - Add CAPTCHA for sensitive operations

## Admin Features

### Download Any User's Models
✅ **Implemented**: Admins can download trained models from any user
- Download button appears in Projects tab for completed projects
- Admin bypass: No ownership check for admins
- Regular users: Can only download their own models

### How It Works
1. Admin views Projects tab
2. Completed projects show "Download" button
3. Click to download model bundle (model.pth + predict.py + labels.json)
4. Works for any user's project

## Future Enhancements

- [ ] User management (edit, delete, suspend)
- [ ] Project management (restart failed, delete)
- [ ] System health monitoring (agent status, uptime)
- [ ] Export data to CSV/Excel
- [ ] Advanced filtering and search
- [ ] Real-time updates with WebSocket
- [ ] Email notifications for admin alerts
- [ ] Detailed analytics and charts
- [ ] Backup and restore functionality

## Testing

1. **Start all services**:
   ```bash
   # Backend
   cd backend && npm start
   
   # MCP Server
   cd mcp_server && python main.py
   ```

2. **Login to frontend**

3. **Click "Admin" tab**

4. **Verify data loads**:
   - Statistics cards show counts
   - Users table populated
   - Projects table populated
   - Logs table populated

## Troubleshooting

### "Failed to load admin data"

**Cause**: Admin key mismatch or missing

**Solution**:
1. Check `ADMIN_KEY` in both `.env` files
2. Restart backend and MCP server
3. Clear browser cache

### "Invalid admin key"

**Cause**: Admin key not matching

**Solution**:
1. Verify `ADMIN_KEY` is same in:
   - `backend/.env`
   - `mcp_server/.env`
2. Restart services

### Empty tables

**Cause**: No data in database yet

**Solution**:
- Create some projects first
- Wait for agents to process
- Check database connection

## Summary

✅ **Admin panel implemented** with comprehensive system overview
✅ **4 main sections**: Stats, Users, Projects, Logs
✅ **Simple authentication** with admin key
✅ **Responsive design** works on all devices
✅ **Real-time data** fetched from database
✅ **Easy to use** tab-based interface

The admin panel provides complete visibility into the AutoML system! 🎉
