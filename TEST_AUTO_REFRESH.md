# Testing Auto-Refresh Feature

## Quick Test Guide

### Prerequisites
1. Backend running on port 4000
2. Frontend running on port 5173
3. Dataset Agent running on port 8002
4. MCP Server running on port 8000

### Test Steps

#### 1. Start All Services

```bash
# Terminal 1 - Backend
cd backend
npm start

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - MCP Server
cd mcp_server
python main.py

# Terminal 4 - Dataset Agent
cd Dataset_Agent/agents/dataset
python main.py
```

#### 2. Open Frontend

Navigate to: `http://localhost:5173`

#### 3. Create a Test Project

In the ML Chat, type:
```
Create a flower classification model with dataset not more than 2GB
```

#### 4. Watch Auto-Refresh in Action

You should see:

1. **Immediately after creation**:
   - Project card appears with status badge
   - Status: "Pending Dataset" (yellow/orange)
   - Green blinking dot appears (auto-refresh active)

2. **Within 5-10 seconds** (Dataset Agent picks it up):
   - "Updating..." badge appears briefly
   - Agent pipeline shows Dataset Agent as active (blue, pulsing)
   - Status updates automatically

3. **After dataset upload** (1-3 minutes):
   - "Updating..." badge appears
   - Status changes to "Pending Training" (blue)
   - Dataset Agent shows as completed (green checkmark)
   - Training Agent shows as active

4. **No manual refresh needed!**
   - All updates happen automatically
   - You can watch the progress in real-time

#### 5. Verify Auto-Refresh Stops

Once project reaches `completed` or `failed`:
- Auto-refresh continues for other active projects
- If no active projects, polling continues but has no effect

### Expected Behavior

✅ **Status updates automatically every 5 seconds**
✅ **"Updating..." indicator shows during refresh**
✅ **Green blinking dot indicates auto-refresh is active**
✅ **No page reload needed**
✅ **Smooth animations during updates**

### Troubleshooting

#### Auto-refresh not working?

1. **Check browser console** for errors:
   ```
   F12 → Console tab
   ```

2. **Verify API is responding**:
   ```bash
   curl http://localhost:4000/api/ml/projects
   ```

3. **Check if projects are in active state**:
   - Auto-refresh only polls if status is:
     - `pending_dataset`
     - `pending_training`
     - `pending_evaluation`

#### Status not updating in database?

1. **Check Dataset Agent logs**:
   - Look for "Status updated successfully"
   - Check for any errors

2. **Run database check**:
   ```bash
   python check-database-status.py
   ```

3. **Verify Dataset Agent is running**:
   ```bash
   curl http://localhost:8002/health
   ```

### Performance Check

Monitor network tab (F12 → Network):
- Should see API calls every 5 seconds when projects are active
- Calls should be fast (< 100ms typically)
- No calls when no active projects

### Success Criteria

✅ Project status updates without manual refresh
✅ Visual indicators show when updating
✅ No console errors
✅ Smooth user experience
✅ Efficient polling (only when needed)

## Advanced Testing

### Test Multiple Projects

1. Create 3 projects in quick succession
2. Watch all 3 update automatically
3. Verify each shows correct status

### Test Error Handling

1. Stop the backend
2. Watch for error messages
3. Restart backend
4. Verify auto-refresh resumes

### Test Performance

1. Create 10+ projects
2. Monitor CPU/memory usage
3. Verify smooth performance
4. Check network traffic is reasonable

## Comparison: Before vs After

### Before (Manual Refresh)
- ❌ User must refresh page to see updates
- ❌ No indication of progress
- ❌ Poor user experience
- ❌ Users don't know when to check back

### After (Auto-Refresh)
- ✅ Updates appear automatically
- ✅ Visual progress indicators
- ✅ Smooth, modern experience
- ✅ Users can watch progress in real-time
