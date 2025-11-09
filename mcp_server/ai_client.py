import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel('gemini-2.5-pro')

def generate_from_prompt(prompt: str, context: list[dict], user_name: str = None):
    """
    Generates a response from the Gemini model.
    """
    # System prompt to define AI behavior
    system_prompt = """You are a helpful AI assistant. Be polite, professional, and helpful. 
    Do not roleplay as characters or pretend to be someone else. 
    Provide clear, accurate, and useful responses to user questions and requests.
    Keep your responses conversational but professional."""
    
    # Build user context
    user_context = ""
    if user_name:
        user_context = f"The user's name is {user_name}. "
    
    # Build context string from chat history
    context_str = ""
    if context:
        # Use all messages for context (remove the 5 message limit)
        for message in context:
            role = "Assistant" if message['role'] == 'assistant' else "User"
            context_str += f"{role}: {message['content']}\n"
    
    # Combine all context with proper system prompt
    if context_str:
        full_prompt = f"{system_prompt}\n\n{user_context}Previous conversation:\n{context_str}\nCurrent message: {prompt}"
    else:
        full_prompt = f"{system_prompt}\n\n{user_context}Current message: {prompt}"

    # Use simple generate_content instead of chat
    response = model.generate_content(full_prompt)
    return response.text
