from supabase_client import get_or_create_user

def get_user_profile(firebase_uid: str, email: str = None, name: str = None):
    """
    Gets the user profile from the database.
    If the user does not exist, it creates a new user.
    """
    return get_or_create_user(firebase_uid, email, name)
