# Development & QA Stories — Detailed (Actionable for Gemini CLI)

**Purpose:** This document expands the earlier high-level stories into *concrete, ordered, and testable steps* so a code-generation agent (Gemini CLI) can scaffold and implement the project end-to-end. Each story contains implementation notes, expected files, acceptance criteria, and test ideas.

> Conventions/assumptions
>
> * Node.js >= 18, npm or yarn. React 18+ (Vite or Create React App).
> * Use Firebase Web SDK for frontend auth and `firebase-admin` on backend.
> * Session approach: HTTPS-only HttpOnly session cookies created on the backend.
> * Local development: Firebase Emulator Suite available for auth + firestore testing.

---

# 1. Repo layout & initial scaffold

**Goal:** Create a mono-repo structure so frontend and backend are isolated but can be started independently.

**Tasks**

1. Create repository root with `package.json` that contains a few helpful scripts and top-level README. (Optional: add workspace config if using pnpm/yarn workspaces.)
2. Create `frontend/` and `backend/` folders with their own `package.json`.
3. Create a `docs/` folder and add `ARCHITECTURE.md`, `openapi.yaml`, `STORIES.md`, and `WIREFRAMES.md`.

**Files to create**

```
/README.md
/frontend/package.json
/frontend/vite.config.js (or CRA files)
/frontend/src/main.jsx
/frontend/src/App.jsx
/backend/package.json
/backend/src/index.js
/backend/src/routes/session.js
/backend/src/middleware/verifySession.js
/docs/STORIES.md
```

**Acceptance criteria**

* `npm run start:frontend` launches the React dev server.
* `npm run start:backend` launches backend on default port (4000).

---

# 2. Environment & Config

**Goal:** Define environment variables and config files required for both frontend and backend.

**Env variables (backend)**

* `FIREBASE_PROJECT_ID` (project id)
* `GOOGLE_APPLICATION_CREDENTIALS` (path to service account JSON) **OR** `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY` (for CI secrets)
* `SESSION_COOKIE_NAME` (e.g. `__session`)
* `SESSION_EXPIRES_IN` (milliseconds, e.g. 5 \* 24 \* 60 \* 60 \* 1000 for 5 days)
* `NODE_ENV`
* `PORT`

**Env variables (frontend)**

* `VITE_API_BASE_URL` (e.g. `http://localhost:4000`)
* `VITE_FIREBASE_API_KEY`
* `VITE_FIREBASE_AUTH_DOMAIN`
* `VITE_FIREBASE_PROJECT_ID`
* `VITE_FIREBASE_APP_ID`
* `VITE_RECAPTCHA_SITE_KEY` (if needed)

**Tasks**

* Add `.env.example` files in both frontend and backend listing required variables.
* Add instructions in README to fill them or to use secrets in CI.

**Acceptance criteria**

* Running backend with missing critical env variables should print a helpful error and exit.

---

# 3. Backend: Core Auth API (DS-1 / DS-2 / DS-3)

**Goal:** Implement three core endpoints and necessary middleware to verify sessions and manage user records.

**Endpoints** (map to `openapi.yaml`)

* `POST /api/sessionLogin` — Accepts `{ idToken }`, verifies it, creates session cookie, upserts user profile in Firestore.
* `POST /api/sessionLogout` — Clears session cookie (set cookie with expires=Thu, 01 Jan 1970 00:00:00 GMT) and revokes session if necessary.
* `GET /api/me` — Reads session cookie, verifies session, returns user profile from Firestore.

**Implementation details**

1. Initialize Firebase Admin SDK at `backend/src/firebase.js` using either service account JSON or env-injected keys. Export `admin` object.
2. Implement `createSessionCookie` logic (use `admin.auth().createSessionCookie(idToken, {expiresIn})`).

   * Set cookie options: `httpOnly: true`, `secure: NODE_ENV === 'production'`, `sameSite: 'strict'`, `maxAge: expiresIn`.
3. Implement `verifySession` middleware which reads cookie name from `SESSION_COOKIE_NAME` and calls `admin.auth().verifySessionCookie(sessionCookie)` (or `verifyIdToken` if using ID tokens) to get `uid`.
4. Implement Firestore helper `userService.upsertFromDecodedToken(decodedToken)` that ensures a `users/{uid}` doc exists with fields (`email`, `phoneNumber`, `displayName`, `photoURL`, `providers`, `lastLogin`, `createdAt`).
5. Rate-limit `/api/sessionLogin` requests to mitigate abuse.

**Files to create**

```
/backend/src/firebase.js
/backend/src/index.js (express app)
/backend/src/routes/session.js
/backend/src/middleware/verifySession.js
/backend/src/services/userService.js
/backend/src/utils/cookieUtils.js
/backend/tests/session.test.js
```

**Acceptance criteria (backend)**

* Sending a valid `idToken` to `/api/sessionLogin` returns 200 and sets cookie header with `Set-Cookie`.
* After login, `GET /api/me` returns the Firestore `users/{uid}` document.
* `/api/sessionLogout` clears the cookie and `/api/me` returns 401.

**Test ideas**

* Unit test `userService.upsertFromDecodedToken` using a fake decoded token.
* Integration test: start the emulator and test full flow using `supertest`.

---

# 4. Frontend: React + Firebase integration (DS-4 / DS-5 / DS-6)

**Goal:** Create the login UI and implement three auth providers and account-linking UI.

**Top-level components**

* `src/pages/LoginPage.jsx` — contains three flows in UI.
* `src/components/PhoneAuth.jsx` — handles phone input, reCAPTCHA, and OTP flow.
* `src/components/OTPModal.jsx` — OTP input and submission.
* `src/components/GoogleSignIn.jsx` — handles popup sign-in and token exchange.
* `src/components/EmailAuth.jsx` — sign up & sign in forms.
* `src/pages/Dashboard.jsx` — shows profile and link/unlink options.
* `src/services/api.js` — wrapper for fetch/axios that sends/receives cookies.

**Implementation details**

1. Initialize Firebase in `frontend/src/firebaseClient.js` using VITE\_ env variables.
2. Phone OTP flow (detailed):

   * Render `RecaptchaVerifier` element in the component (use `window.recaptchaVerifier` for modular SDK clarity).
   * Call `signInWithPhoneNumber(auth, phoneNumber, recaptchaVerifier)` which returns `confirmationResult`.
   * Prompt user for OTP → call `confirmationResult.confirm(code)` → returns a `userCredential` with `user` object.
   * Call `user.getIdToken()` → send `{ idToken }` to backend `/api/sessionLogin` using `fetch` with `credentials: 'include'` to receive the cookie.
3. Google Sign-in flow:

   * Use `signInWithPopup(auth, new GoogleAuthProvider())` → `userCredential` → `user.getIdToken()` → same POST to backend.
4. Email/Password:

   * For sign up use `createUserWithEmailAndPassword(auth, email, password)`; for sign in use `signInWithEmailAndPassword`.
   * After login get ID token and POST to `/api/sessionLogin`.
5. Account linking:

   * If user currently has an active client-side Firebase `user`, provide an option to link another provider:

     * For example, if user logged in with email, clicking "Link Google" triggers `linkWithPopup` or `linkWithCredential` depending on provider.
     * After successful `linkWithCredential`, ensure backend sees updated providers: call `user.getIdToken(true)` and POST to `/api/sessionLogin` to refresh server session & user record.
6. Important: Do not rely solely on client auth state for protected pages. Always call `GET /api/me` to fetch the authoritative server profile.

**Files to create**

```
/frontend/src/firebaseClient.js
/frontend/src/pages/LoginPage.jsx
/frontend/src/components/PhoneAuth.jsx
/frontend/src/components/OTPModal.jsx
/frontend/src/components/GoogleSignIn.jsx
/frontend/src/components/EmailAuth.jsx
/frontend/src/pages/Dashboard.jsx
/frontend/src/services/api.js
/frontend/src/App.jsx
/frontend/src/main.jsx
```

**Acceptance criteria (frontend)**

* User can sign in with phone, google, and email/password and receives a server-side cookie.
* After login the dashboard shows correct user profile data fetched from `/api/me`.
* Linking another provider updates the `providers` array stored in Firestore and reflected on `/api/me`.

**Test ideas**

* Unit test components logic with React Testing Library.
* E2E test: simulate phone OTP using Firebase Emulator, verify end-to-end flow from frontend to `/api/me`.

---

# 5. Firestore rules & Initialization

**Goal:** Strong, minimal security rules so users can only access their own documents.

**Files**

* `firebase.rules` (Firestore rules)

**Rules (MVP)**

```js
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{uid} {
      allow read, update: if request.auth != null && request.auth.uid == uid;
      allow create: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

**Tasks**

* Add `firebase.json` that configures the emulator and rules file.
* Document how to import seeded user docs (if desired) or how the backend will create them on first login.

**Acceptance criteria**

* When the emulator is started, frontend cannot read other users' documents.

---

# 6. Testing & Emulators

**Goal:** Configure tests and local emulator flows for reliable development and CI.

**Tasks**

1. Add `backend/package.json` scripts:

   * `test` for unit tests (jest)
   * `start` to start express
   * `start:dev` with nodemon
2. Add `frontend/package.json` scripts:

   * `start` for dev server
   * `build` for production
3. Add `scripts` in root `package.json` to start both frontend and backend concurrently (optional).
4. Provide a `dev` script to start Firebase Emulator: `firebase emulators:start --only auth,firestore`.
5. Write an integration test that:

   * Starts emulator (CI: use `firebase emulators:exec`) or uses pre-seeded emulator state.
   * Runs a simulated phone sign-in using emulator hooks.
   * Calls backend endpoints with tokens issued by emulator.

**Test stacks**

* Unit tests: Jest + Supertest (backend), React Testing Library (frontend).
* E2E: Playwright or Cypress integrated with Firebase emulator.

**Acceptance criteria**

* CI runs unit tests and at least one basic integration test against emulator.

---

# 7. Account linking story (detailed)

**Goal:** Allow a user to combine multiple providers into one account safely.

**Steps**

1. Client has signed in with provider A (e.g., phone). On dashboard, show "Link another method".
2. If user selects Google:

   * Use `linkWithPopup(auth, googleProvider)` (client-side) — if provider already linked to *another* account, handle `auth/account-exists-with-different-credential` error.
   * On success, get fresh ID token and POST to `/api/sessionLogin` to refresh server session and store updated providers.
3. For email linking (linking a password to an existing phone account), create credential with `EmailAuthProvider.credential(email, password)` and call `linkWithCredential()`.
4. For phone linking, use `PhoneAuthProvider` to get `verificationId`, then `PhoneAuthProvider.credential(verificationId, code)` and call `linkWithCredential()`.

**Edge cases & error handling**

* If linking fails because the provider is associated with another account, present an option to *merge accounts*—but merging requires careful flow (out of scope for MVP). Instead, show a helpful message: "This Google account is already linked to another account. Please log in with Google first and then link your phone/email."

**Acceptance criteria**

* After linking, `/api/me` returns `providers` array containing the new provider.

---

# 8. Logging, Monitoring & Error handling

**Goal:** Provide a minimal logging + error strategy.

**Tasks**

* Use `winston` or simple console logs on backend, categorize logs (info, warn, error).
* Log failed auth attempts (without logging PII like OTP codes or passwords).
* Return consistent error shapes from the API (e.g. `{ error: { code: 'UNAUTHORIZED', message: '...' } }`).

**Acceptance criteria**

* Errors from `/api/sessionLogin` return 4xx on bad tokens and log a warn-level entry.

---

# 9. CI & Definition of Done (DoD)

**Minimum CI checks**

* `npm test` passes for both frontend & backend.
* Linting passes (ESLint) and code formatting (Prettier).
* Built frontend (vite build) completes without error.
* Optional: run at least one integration test against the Firebase emulator via `firebase emulators:exec "npm test:integration"`.

**Definition of Done for a story**

* Code pushed to a feature branch.
* Unit tests added and passing for new code.
* Manual E2E validation documented or automated test added.
* README updated if any setup steps changed.

---

# 10. Suggested Implementation Order (Sprint style)

**Sprint 1 (Scaffold + Backend base)**

* Repo scaffold, backend Express server, Firebase Admin init, `POST /api/sessionLogin` logic, `userService.upsertFromDecodedToken`.
* Tests: unit test userService.

**Sprint 2 (Frontend basics + session)**

* Basic React scaffold, firebase client init, Email/Password sign-up & sign-in, token exchange to `/api/sessionLogin`, `/api/me` endpoint.
* Tests: simple React unit tests.

**Sprint 3 (Phone OTP + reCAPTCHA + linking)**

* Implement PhoneAuth UI, OTP modal, OTP confirm flow, linking UI.
* Tests: e2e using emulator.

**Sprint 4 (Polish + Tests + CI)**

* Implement logout, session cookie security flags, Firestore rules, CI integration and emulator-based integration tests.

---

# 11. Developer notes for Gemini CLI

* Prefer modular Firebase SDK usage (frontend) and `firebase-admin` (backend).
* Keep all secrets out of code. Use `.env` for local testing and CI secrets for pipelines.
* Use the provided `openapi.yaml` as a contract to generate route handlers and validation stubs.
* Make sure `fetch` calls to backend include `credentials: 'include'` to send cookies.

---

# 12. Appendix: Example `POST /api/sessionLogin` Flow (Pseudo-code)

```js
// Accept { idToken }
const decoded = await admin.auth().verifyIdToken(idToken);
// create session cookie
const expiresIn = Number(process.env.SESSION_EXPIRES_IN) || 5*24*60*60*1000;
const sessionCookie = await admin.auth().createSessionCookie(idToken, { expiresIn });
res.cookie(process.env.SESSION_COOKIE_NAME, sessionCookie, {
  maxAge: expiresIn,
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict'
});
// Upsert user
await userService.upsertFromDecodedToken(decoded);
res.json({ status: 'ok', uid: decoded.uid });
```

---

