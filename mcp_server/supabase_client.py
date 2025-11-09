import os
from supabase import create_client, Client

supabase: Client = None

def init_supabase(url: str, key: str):
    global supabase
    supabase = create_client(url, key)

def get_or_create_user(firebase_uid: str, email: str = None, name: str = None):
    print(f"DEBUG: get_or_create_user called with firebase_uid={firebase_uid}, email={email}, name={name}")
    
    # First, try to get existing user with all fields
    response = supabase.table('users').select('*').eq('firebase_uid', firebase_uid).execute()
    print(f"DEBUG: Existing user query result: {response.data}")
    
    if response.data:
        existing_user = response.data[0]
        print(f"DEBUG: Found existing user: {existing_user}")
        
        # Update user if we have new email/name info and they're missing
        if (email and not existing_user.get('email')) or (name and not existing_user.get('name')):
            update_data = {}
            if email and not existing_user.get('email'):
                update_data['email'] = email
            if name and not existing_user.get('name'):
                update_data['name'] = name
            
            if update_data:
                print(f"DEBUG: Updating user with data: {update_data}")
                supabase.table('users').update(update_data).eq('firebase_uid', firebase_uid).execute()
                # Return updated user
                response = supabase.table('users').select('*').eq('firebase_uid', firebase_uid).execute()
                print(f"DEBUG: Updated user result: {response.data[0]}")
                return response.data[0]
        
        return existing_user
    else:
        # Create new user
        user_data = {
            'firebase_uid': firebase_uid,
            'email': email,
            'name': name
        }
        print(f"DEBUG: Creating new user with data: {user_data}")
        response = supabase.table('users').insert(user_data).execute()
        print(f"DEBUG: New user created: {response.data[0]}")
        return response.data[0]

def store_message(user_id: str, role: str, content: str, metadata: dict = None):
    message_data = {
        'user_id': user_id,
        'role': role,
        'content': content,
        'metadata': metadata
    }
    response = supabase.table('messages').insert(message_data).execute()
    return response.data[0]

def get_recent_messages(user_id: str, limit: int = None):
    # Get the most recent messages (newest first)
    query = supabase.table('messages').select('*').eq('user_id', user_id).order('created_at', desc=True)
    
    if limit:
        query = query.limit(limit)
    
    response = query.execute()
    print(f"DEBUG: Raw database response: {response.data}")
    # Reverse to get chronological order (oldest first)
    reversed_data = list(reversed(response.data))
    print(f"DEBUG: Reversed data: {reversed_data}")
    return reversed_data

def clear_user_messages(user_id: str):
    """
    Deletes all messages for a specific user.
    """
    print(f"DEBUG: Clearing all messages for user_id: {user_id}")
    response = supabase.table('messages').delete().eq('user_id', user_id).execute()
    print(f"DEBUG: Clear messages response: {response}")
    return response

def get_supabase_client():
    """
    Returns the initialized Supabase client.
    """
    global supabase
    if supabase is None:
        raise Exception("Supabase client not initialized. Call init_supabase() first.")
    return supabase
