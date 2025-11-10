-- Add is_admin column to existing users table
-- This is safe to run - it won't delete any data

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_admin boolean DEFAULT false;

-- Optional: Make yourself admin (replace with your Firebase UID)
-- UPDATE users 
-- SET is_admin = true 
-- WHERE firebase_uid = 'YOUR_FIREBASE_UID_HERE';

-- To find your Firebase UID, run:
-- SELECT id, firebase_uid, email, is_admin FROM users;
