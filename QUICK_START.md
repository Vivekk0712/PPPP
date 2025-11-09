# Quick Start Guide

## Test the New Frontend Features

### Prerequisites
Make sure all three services are running:
1. ✅ Backend (port 4000)
2. ✅ MCP Server (port 8000)
3. ✅ Frontend (port 5173)

## Step-by-Step Testing

### 1. Login
- Open http://localhost:5173
- Sign in with Google, Email, or Phone
- You should see the new dashboard

### 2. Explore Home Tab
- See the welcome message with your name
- Notice three gradient cards:
  - 🔮 ML Projects (Purple)
  - 🖼️ Test Models (Orange)
  - 💬 AI Assistant (Green)
- Click on any card to navigate

### 3. Test ML Projects Tab

#### Create a Project
1. Click "ML Projects" tab or card
2. You'll see:
   - ML Chat Assistant on the left (purple gradient)
   - Your Projects list on the right
3. Try an example prompt or type your own:
   - "Train a model to classify plant diseases"
   - "Create an image classifier for skin cancer detection"
4. Click Send
5. Watch the project appear in the list!

#### View Project Details
1. Click "View Details" on any project card
2. See the agent pipeline visualization:
   - Planner → Dataset → Training → Evaluation
   - Active agents pulse with animation
3. Check the Details and Metadata tabs
4. Close the modal

### 4. Test Model Tab

#### Upload and Test
1. Click "Test Model" tab
2. Select a model from dropdown (only completed models show)
3. Upload an image:
   - Click the upload area
   - Or drag and drop an image
4. See the image preview
5. Click "Test Model"
6. View prediction results (when backend is implemented)

### 5. Test General Chat

#### On Home Tab
1. Go back to "Home" tab
2. Click the chat icon in top navigation
3. A floating chat widget appears
4. Type a message and send
5. Toggle fullscreen mode
6. Clear chat history if needed

### 6. Test Profile

#### Update Profile
1. Click the Profile icon (person icon) in top navigation
2. Modal overlay appears
3. Update your name or phone number
4. Click "Save Changes"
5. See the updated name in welcome message

### 7. Test Responsive Design

#### Mobile View
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select a mobile device
4. Navigate through all tabs
5. Everything should work smoothly

## What You Should See

### Visual Elements
✅ Smooth animations on page load
✅ Gradient backgrounds on cards
✅ Hover effects on buttons and cards
✅ Progress bars on active projects
✅ Status badges with colors
✅ Loading spinners during API calls
✅ Beautiful modal overlays
✅ Responsive layout on all screens

### Interactions
✅ Tab navigation works
✅ Buttons respond to clicks
✅ Forms submit correctly
✅ Modals open and close
✅ Chat messages send and display
✅ Images upload and preview
✅ Dropdowns work
✅ Scrolling is smooth

## Expected Behavior

### When Creating a Project
1. Message appears in chat
2. Loading spinner shows
3. Response appears
4. Project card appears in list
5. Status shows "Pending Dataset"
6. Progress bar at 25%

### When Viewing Details
1. Modal slides in
2. Agent pipeline animates
3. Active agent pulses
4. Tabs switch smoothly
5. Data displays correctly

### When Testing Model
1. Image uploads
2. Preview shows
3. Loading spinner during test
4. Results display (when implemented)

## Troubleshooting

### No Projects Showing
- Check browser console for errors
- Verify MCP server is running
- Check Supabase connection
- Look at backend logs

### Chat Not Working
- Verify backend is running
- Check MCP_SERVER_URL in backend .env
- Look for CORS errors in console

### Images Not Uploading
- Check file size (< 10MB)
- Verify file type (PNG, JPG, JPEG)
- Check browser console for errors

### Styling Issues
- Clear browser cache
- Check if App.css loaded
- Verify Bootstrap CSS is imported
- Check for console errors

## Testing Checklist

### Navigation
- [ ] Home tab loads
- [ ] ML Projects tab loads
- [ ] Test Model tab loads
- [ ] Tab switching works
- [ ] Back button works

### ML Projects
- [ ] Chat interface loads
- [ ] Example prompts work
- [ ] Can send custom message
- [ ] Project appears in list
- [ ] Project card displays correctly
- [ ] View Details opens modal
- [ ] Modal shows pipeline
- [ ] Can close modal

### Model Testing
- [ ] Model dropdown populates
- [ ] Can select model
- [ ] Can upload image
- [ ] Image preview shows
- [ ] Can remove image
- [ ] Test button enables/disables correctly

### General Features
- [ ] Profile modal opens
- [ ] Can update profile
- [ ] Chat widget works
- [ ] Can toggle fullscreen
- [ ] Can clear chat
- [ ] Logout works
- [ ] Responsive on mobile

### Visual Quality
- [ ] Gradients render correctly
- [ ] Animations are smooth
- [ ] No layout shifts
- [ ] Colors are consistent
- [ ] Text is readable
- [ ] Icons display properly

## Demo Flow

### For Presentation
1. **Login** - Show authentication
2. **Home** - Highlight the three main features
3. **ML Projects** - Create a project with chat
4. **Project Card** - Show status and details
5. **Pipeline** - Demonstrate agent visualization
6. **Test Model** - Upload and test (mock result)
7. **Profile** - Update user info
8. **Responsive** - Show mobile view

## Next Actions

After testing the UI:
1. ✅ Confirm all UI elements work
2. ⏳ Implement Planner Agent logic
3. ⏳ Connect Dataset Agent to Kaggle
4. ⏳ Build Training Agent
5. ⏳ Create Evaluation Agent
6. ⏳ Add model download
7. ⏳ Implement model testing

## Support

If something doesn't work:
1. Check all three services are running
2. Review browser console for errors
3. Check backend terminal for logs
4. Check MCP server terminal for logs
5. Verify environment variables are set
6. Clear browser cache and reload

## Enjoy! 🎉

You now have a beautiful, professional AutoML platform UI ready to go!
