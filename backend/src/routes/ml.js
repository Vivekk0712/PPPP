const express = require('express');
const router = express.Router();
const axios = require('axios');
const verifySession = require('../middleware/verifySession');

const MCP_SERVER_URL = process.env.MCP_SERVER_URL || 'http://127.0.0.1:8000';

// Create ML project via chat
router.post('/ml/chat', verifySession, async (req, res) => {
  try {
    const { message } = req.body;
    const firebaseUid = req.user.uid;
    const userName = req.user.name || req.user.email;
    const userEmail = req.user.email;

    console.log(`ML Chat request from user ${firebaseUid}: ${message}`);

    // Forward to MCP server's planner agent endpoint
    const mcpResponse = await axios.post(`${MCP_SERVER_URL}/api/ml/planner`, {
      user_id: firebaseUid,
      message,
      user_name: userName,
      user_email: userEmail
    });

    res.json(mcpResponse.data);
  } catch (error) {
    console.error('Error in ML chat:', error.message);
    res.status(500).json({ 
      error: 'Failed to process ML request',
      details: error.response?.data || error.message 
    });
  }
});

// Get all ML projects for user
router.get('/ml/projects', verifySession, async (req, res) => {
  try {
    const firebaseUid = req.user.uid;
    
    console.log(`Fetching ML projects for user ${firebaseUid}`);

    const mcpResponse = await axios.get(`${MCP_SERVER_URL}/api/ml/projects`, {
      params: { user_id: firebaseUid }
    });

    res.json(mcpResponse.data);
  } catch (error) {
    console.error('Error fetching ML projects:', error.message);
    res.status(500).json({ 
      error: 'Failed to fetch projects',
      details: error.response?.data || error.message 
    });
  }
});

// Get specific ML project by ID
router.get('/ml/projects/:projectId', verifySession, async (req, res) => {
  try {
    const { projectId } = req.params;
    const firebaseUid = req.user.uid;

    console.log(`Fetching project ${projectId} for user ${firebaseUid}`);

    const mcpResponse = await axios.get(`${MCP_SERVER_URL}/api/ml/projects/${projectId}`, {
      params: { user_id: firebaseUid }
    });

    res.json(mcpResponse.data);
  } catch (error) {
    console.error('Error fetching project:', error.message);
    res.status(500).json({ 
      error: 'Failed to fetch project',
      details: error.response?.data || error.message 
    });
  }
});

// Get project logs
router.get('/ml/projects/:projectId/logs', verifySession, async (req, res) => {
  try {
    const { projectId } = req.params;
    const firebaseUid = req.user.uid;

    console.log(`Fetching logs for project ${projectId}`);

    const mcpResponse = await axios.get(`${MCP_SERVER_URL}/api/ml/projects/${projectId}/logs`, {
      params: { user_id: firebaseUid }
    });

    res.json(mcpResponse.data);
  } catch (error) {
    console.error('Error fetching project logs:', error.message);
    res.status(500).json({ 
      error: 'Failed to fetch logs',
      details: error.response?.data || error.message 
    });
  }
});

// Download model
router.get('/ml/projects/:projectId/download', verifySession, async (req, res) => {
  try {
    const { projectId } = req.params;
    const firebaseUid = req.user.uid;

    console.log(`Downloading model for project ${projectId}`);

    const mcpResponse = await axios.get(`${MCP_SERVER_URL}/api/ml/projects/${projectId}/download`, {
      params: { user_id: firebaseUid },
      responseType: 'stream'
    });

    // Forward the stream to client
    res.setHeader('Content-Type', mcpResponse.headers['content-type']);
    res.setHeader('Content-Disposition', mcpResponse.headers['content-disposition']);
    mcpResponse.data.pipe(res);
  } catch (error) {
    console.error('Error downloading model:', error.message);
    res.status(500).json({ 
      error: 'Failed to download model',
      details: error.response?.data || error.message 
    });
  }
});

// Test model with image
router.post('/ml/projects/:projectId/test', verifySession, async (req, res) => {
  try {
    const { projectId } = req.params;
    const firebaseUid = req.user.uid;

    console.log(`Testing model for project ${projectId}`);

    // Forward multipart form data to MCP server
    const FormData = require('form-data');
    const formData = new FormData();
    
    if (req.files && req.files.image) {
      formData.append('image', req.files.image.data, req.files.image.name);
    } else if (req.file) {
      formData.append('image', req.file.buffer, req.file.originalname);
    }
    
    formData.append('user_id', firebaseUid);

    const mcpResponse = await axios.post(
      `${MCP_SERVER_URL}/api/ml/projects/${projectId}/test`,
      formData,
      {
        headers: formData.getHeaders()
      }
    );

    res.json(mcpResponse.data);
  } catch (error) {
    console.error('Error testing model:', error.message);
    res.status(500).json({ 
      error: 'Failed to test model',
      details: error.response?.data || error.message 
    });
  }
});

module.exports = router;
