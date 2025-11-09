from supabase_client import get_or_create_user, get_recent_messages, store_message as supabase_store_message, clear_user_messages

def get_chat_history(firebase_uid: str, limit: int = None):
    """
    Gets the chat history for a given user.
    If limit is None, fetches all messages.
    """
    user = get_or_create_user(firebase_uid)
    if limit is None:
        return get_recent_messages(user['id'])
    return get_recent_messages(user['id'], limit)

def store_message(firebase_uid: str, role: str, content: str):
    """
    Stores a message in the database.
    """
    user = get_or_create_user(firebase_uid)
    return supabase_store_message(user['id'], role, content)

def clear_chat_history(firebase_uid: str):
    """
    Clears all chat history for a given user.
    """
    user = get_or_create_user(firebase_uid)
    return clear_user_messages(user['id'])
