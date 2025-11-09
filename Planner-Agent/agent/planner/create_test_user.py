"""
Create a test user in Supabase for testing
"""
import os
from supabase import create_client
from dotenv import load_dotenv
import uuid

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Create a test user
test_user_id = str(uuid.uuid4())
test_email = "test@example.com"

try:
    # Try to insert a test user
    result = supabase.table("users").insert({
        "id": test_user_id,
        "email": test_email,
        "created_at": "now()"
    }).execute()
    
    print(f"✅ Test user created successfully!")
    print(f"User ID: {test_user_id}")
    print(f"Email: {test_email}")
    print(f"\nUse this user_id in your tests:")
    print(f'  "user_id": "{test_user_id}"')
    
except Exception as e:
    print(f"Error creating test user: {e}")
    print("\nTrying to fetch existing users...")
    
    try:
        result = supabase.table("users").select("id, email").limit(1).execute()
        if result.data:
            user = result.data[0]
            print(f"✅ Found existing user:")
            print(f"User ID: {user['id']}")
            print(f"Email: {user.get('email', 'N/A')}")
            print(f"\nUse this user_id in your tests:")
            print(f'  "user_id": "{user["id"]}"')
        else:
            print("No users found in database.")
    except Exception as e2:
        print(f"Error fetching users: {e2}")
