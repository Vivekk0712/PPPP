# Wireframes (Textual Descriptions)

## Login Screen
- Title: *"Welcome to AuthApp"*
- Options:
  - Phone OTP Login button
  - Google Sign-In button
  - Email/Password form
    - Email input
    - Password input
    - Sign In button
    - "Create account" link

---

## Phone OTP Flow
- Step 1: Input for phone number (`+91 XXXXXXXX`) + "Send OTP" button.
- Step 2: OTP input field (6 digits) + "Verify" button.
- Success → redirect to dashboard.

---

## Google Sign-In Flow
- Single "Sign in with Google" button.
- Opens Google popup → consent.
- Success → redirect to dashboard.

---

## Email/Password Flow
### Sign In Form
- Email input
- Password input
- "Sign In" button

### Sign Up Form
- Email input
- Password input (with strength hint)
- "Sign Up" button

---

## Dashboard
- Greeting: "Hello, {displayName or email/phone}"
- User profile section:
  - email
  - phone
  - providers list
- Logout button
- Option: "Link another login method"
