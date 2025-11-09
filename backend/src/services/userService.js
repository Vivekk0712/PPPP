const admin = require('../firebase');

const db = admin.firestore();

async function upsertFromDecodedToken(decodedToken) {
  const { uid, email, phone_number, name, picture } = decodedToken;
  console.log('DEBUG: upsertFromDecodedToken called with:', { uid, email, phone_number, name, picture });
  
  const userRef = db.collection('users').doc(uid);
  const userDoc = await userRef.get();

  const userData = {
    uid,
    lastLogin: new Date().toISOString(),
  };

  if (email) userData.email = email;
  if (phone_number) userData.phoneNumber = phone_number;
  if (name) userData.displayName = name;
  if (picture) userData.photoURL = picture;
  
  console.log('DEBUG: userData to be saved:', userData);

  if (!userDoc.exists) {
    userData.createdAt = new Date().toISOString();
    userData.providers = decodedToken.firebase.identities
      ? Object.keys(decodedToken.firebase.identities)
      : [];
  } else {
    const existingData = userDoc.data();
    const existingProviders = existingData.providers || [];
    const newProviders = decodedToken.firebase.identities
      ? Object.keys(decodedToken.firebase.identities)
      : [];
    
    const mergedProviders = [...new Set([...existingProviders, ...newProviders])];
    userData.providers = mergedProviders;
  }

  await userRef.set(userData, { merge: true });
  return userData;
}

module.exports = {
  upsertFromDecodedToken,
};
