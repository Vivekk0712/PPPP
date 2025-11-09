const admin = require('firebase-admin');
require('dotenv').config();

try {
  admin.initializeApp({
    credential: admin.credential.applicationDefault(),
    projectId: process.env.FIREBASE_PROJECT_ID,
  });
} catch (error) {
  console.error('Firebase Admin SDK initialization error:', error);
  process.exit(1);
}

module.exports = admin;
