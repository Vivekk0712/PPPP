const admin = require('../firebase');

async function verifySession(req, res, next) {
  const sessionCookie = req.cookies[process.env.SESSION_COOKIE_NAME] || '';

  try {
    const decodedClaims = await admin.auth().verifySessionCookie(sessionCookie, true /** checkRevoked */);
    req.user = decodedClaims;
    next();
  } catch (error) {
    res.status(401).json({ error: { code: 'UNAUTHORIZED', message: 'Unauthorized' } });
  }
}

module.exports = verifySession;