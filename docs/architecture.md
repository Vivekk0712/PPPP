# Architecture Document  
**Project:** Firebase Phone + Google + Email/Password Authentication App  
**Author:** Vivek  
**Date:** 2025-09-21  

---

## 1. Overview
This project implements a minimal authentication system using **Firebase Authentication**, **React** (frontend), and **Node.js with Firebase Admin SDK** (backend).  

Users can sign up/sign in using:  
- **Phone OTP (SMS)** with reCAPTCHA verification  
- **Google Sign-In (Gmail)**  
- **Email/Password**  

All methods support **account linking** so a user can log in with any provider under the same Firebase UID.  

---

## 2. Goals
- Provide a simple and secure authentication system.  
- Support **session cookies** on the backend for persistent, secure login.  
- Store basic user profile data in Firestore.  
- Cover three auth providers (Phone, Google, Email/Password).  
- Minimal scope (no admin panel, no deployment configuration).  

---

## 3. System Architecture

### High-Level Diagram

[React Frontend] -- Firebase Web SDK -->
- signInWithPhoneNumber (SMS OTP)
- signInWithPopup (Google)
- createUserWithEmailAndPassword / signInWithEmailAndPassword
-> obtains Firebase ID Token
-> POST /api/sessionLogin (idToken)

[Node.js Backend] -- Firebase Admin SDK -->
- verifyIdToken(idToken)
- createSessionCookie(idToken)
- read/write Firestore user profile

[Firebase Services]
- Firebase Authentication (Phone + Google + Email/Password)
- Firestore Database

markdown
Copy code

---

## 4. Components

### Frontend (React + Firebase Web SDK)
- UI with **Phone OTP login form**, **Google Sign-In button**, and **Email/Password form**.  
- Handles OTP entry and reCAPTCHA for phone login.  
- Uses `linkWithCredential()` for account linking across providers.  
- Sends ID token to backend after login.  

### Backend (Node.js + Express + Firebase Admin SDK)
- Validates ID tokens using `admin.auth().verifyIdToken()`.  
- Creates **secure session cookies** using `admin.auth().createSessionCookie()`.  
- Manages Firestore `users` collection for storing user profiles.  
- Provides REST endpoints:  
  - `POST /api/sessionLogin`  
  - `POST /api/sessionLogout`  
  - `GET /api/me`  

### Firebase
- **Authentication**: Phone, Google, and Email/Password providers enabled.  
- **Firestore**: Stores user profiles.  
- **Security rules**: Users can only access their own data.  

---

## 5. Data Model

**Collection:** `users`  
**Document ID:** `uid`

```json
{
  "uid": "uid123",
  "email": "bob@gmail.com",
  "phoneNumber": "+91XXXXXXXXXX",
  "displayName": "Bob",
  "photoURL": "https://...",
  "providers": ["google.com","phone","password"],
  "createdAt": "2025-09-21T10:00:00Z",
  "lastLogin": "2025-09-21T11:00:00Z"
}
6. Authentication Flows
Phone OTP (Web)
User enters phone → Firebase Web SDK triggers reCAPTCHA.

Firebase sends OTP via SMS.

User enters OTP → Firebase issues ID token.

ID token sent to backend → backend verifies → issues session cookie.

Google Sign-In (Web)
User clicks Google Sign-In → Firebase popup.

Firebase issues ID token.

ID token sent to backend → backend verifies → session cookie created.

Email/Password (Web)
User signs up or logs in with email/password using Firebase SDK (createUserWithEmailAndPassword or signInWithEmailAndPassword).

Firebase issues ID token.

ID token sent to backend → backend verifies → session cookie created.

Account Linking
If signed in with one method, user can link another via linkWithCredential().

All providers point to the same UID.

7. API Endpoints
Endpoint	Method	Description
/api/sessionLogin	POST	Exchange Firebase ID token → session cookie
/api/sessionLogout	POST	Clear session cookie
/api/me	GET	Fetch current user profile (from Firestore)

8. Security Considerations
Phone auth requires reCAPTCHA (to prevent SMS abuse).

Session cookies are HttpOnly, Secure, SameSite=Strict.

Tokens verified with admin.auth().verifyIdToken().

Firestore rules enforce per-user data isolation.

For Email/Password:

Strong password policy enforced in Firebase console.

Optionally enable email verification before login.

9. Testing
Use Firebase Emulator Suite for local testing of phone, Google, and email auth.

Unit test backend API endpoints with mock ID tokens.

E2E tests:

Phone login works → /api/me returns phone number.

Google login works → /api/me returns Gmail.

Email login works → /api/me returns email.

Linking works → /api/me shows multiple providers.

10. Out of Scope
Deployment (Vercel, Netlify, etc.)

Admin dashboard

Role-based access control

Native mobile apps

11. Future Enhancements
Add account recovery and password reset flows.

Add roles (user/admin).

Add support for multi-factor authentication.

Add login activity history for security.