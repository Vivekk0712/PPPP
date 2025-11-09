const express = require('express');
const admin = require('../firebase');
const { upsertFromDecodedToken } = require('../services/userService');
const verifySession = require('../middleware/verifySession');
const axios = require('axios');

const router = express.Router();

router.post('/sessionLogin', async (req, res) => {
  const { idToken } = req.body;

  if (!idToken) {
    return res.status(400).json({ error: { code: 'BAD_REQUEST', message: 'idToken is required' } });
  }

  try {
    const decodedToken = await admin.auth().verifyIdToken(idToken);
    await upsertFromDecodedToken(decodedToken);

    const expiresIn = Number(process.env.SESSION_EXPIRES_IN) || 5 * 24 * 60 * 60 * 1000;
    const sessionCookie = await admin.auth().createSessionCookie(idToken, { expiresIn });

    const options = {
      maxAge: expiresIn,
      httpOnly: true,
      secure: true,
      sameSite: 'None',
    };

    res.cookie(process.env.SESSION_COOKIE_NAME, sessionCookie, options);
    res.json({ status: 'ok', uid: decodedToken.uid });
  } catch (error) {
    console.error('Error in /sessionLogin:', error);
    res.status(401).json({ error: { code: 'UNAUTHORIZED', message: 'Invalid idToken' } });
  }
});

router.post('/sessionLogout', (req, res) => {
  const sessionCookie = req.cookies[process.env.SESSION_COOKIE_NAME] || '';
  res.clearCookie(process.env.SESSION_COOKIE_NAME);

  if (sessionCookie) {
    admin.auth().verifySessionCookie(sessionCookie)
      .then((decodedClaims) => admin.auth().revokeRefreshTokens(decodedClaims.sub))
      .then(() => {
        res.status(200).json({ status: 'ok' });
      })
      .catch((error) => {
        console.error('Error revoking session cookie:', error);
        res.status(200).json({ status: 'ok' }); // Still clear cookie on client
      });
  } else {
    res.status(200).json({ status: 'ok' });
  }
});

router.get('/me', verifySession, async (req, res) => {
    const userRef = admin.firestore().collection('users').doc(req.user.uid);
    const userDoc = await userRef.get();

    if (!userDoc.exists) {
        return res.status(404).json({ error: { code: 'NOT_FOUND', message: 'User not found' } });
    }

    res.json(userDoc.data());
});

router.post('/chat', verifySession, async (req, res) => {
  const { message, metadata } = req.body;
  const firebaseUid = req.user.uid;
  
  // Get user information from Firebase token
  console.log('Firebase token user data:', JSON.stringify(req.user, null, 2));
  let userName = req.user.displayName || req.user.name || null;
  let userEmail = req.user.email || null;
  
  // If name/email not in token, try to get from Firestore
  if (!userName || !userEmail) {
    try {
      const userRef = admin.firestore().collection('users').doc(firebaseUid);
      const userDoc = await userRef.get();
      
      if (userDoc.exists) {
        const userData = userDoc.data();
        console.log('Firestore user data:', userData);
        userName = userName || userData.displayName || userData.name || null;
        userEmail = userEmail || userData.email || null;
      }
    } catch (error) {
      console.error('Error fetching user from Firestore:', error);
    }
  }
  
  console.log('Final extracted - Name:', userName, 'Email:', userEmail);

  try {
    const mcpResponse = await axios.post(process.env.MCP_SERVER_URL + '/mcp/query', {
      user_id: firebaseUid,
      message,
      metadata,
      user_name: userName,
      user_email: userEmail,
    });

    res.json(mcpResponse.data);
  } catch (error) {
    console.error('Error forwarding chat to MCP server:', error);
    res.status(500).json({ error: { code: 'MCP_SERVER_ERROR', message: 'Error forwarding chat to MCP server' } });
  }
});

router.get('/history', verifySession, async (req, res) => {
  const firebaseUid = req.user.uid;

  try {
    const mcpResponse = await axios.get(process.env.MCP_SERVER_URL + '/mcp/history?user_id=' + firebaseUid);
    res.json(mcpResponse.data);
  } catch (error) {
    console.error('Error fetching chat history from MCP server:', error);
    res.status(500).json({ error: { code: 'MCP_SERVER_ERROR', message: 'Error fetching chat history from MCP server' } });
  }
});

router.delete('/clear-chat', verifySession, async (req, res) => {
  const firebaseUid = req.user.uid;

  try {
    const mcpResponse = await axios.delete(process.env.MCP_SERVER_URL + '/mcp/clear-chat?user_id=' + firebaseUid);
    res.json(mcpResponse.data);
  } catch (error) {
    console.error('Error clearing chat history from MCP server:', error);
    res.status(500).json({ error: { code: 'MCP_SERVER_ERROR', message: 'Error clearing chat history from MCP server' } });
  }
});

module.exports = router;