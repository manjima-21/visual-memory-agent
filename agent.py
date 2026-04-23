import os
import time
import streamlit as st
from google import genai
from PIL import Image

# 1. API Key Setup
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Fallback for local testing
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini Client
client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-1.5-flash" 

# 2. Persist Memory in Streamlit Session State
if 'internal_memory' not in st.session_state:
    st.session_state.internal_memory = []

def save_to_memory(observation: str, location: str = "unknown") -> str:
    """Formats and saves a string observation to the session state."""
    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {observation} (Location: {location})"
    st.session_state.internal_memory.append(entry)
    print(f"✨ MEMORY LOGGED: {entry}")
    return "Successfully archived in memory."

def analyze_scene(image_input):
    """Sends image to Gemini and logs the result to memory."""
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=["List the main objects in this image and their specific locations on the desk.", image_input]
        )
        
        analysis_text = response.text
        
        # Save the result into our persistent memory list
        save_to_memory(analysis_text)
        
        return analysis_text
    except Exception as e:
        return f"Error during analysis: {str(e)}"

def get_memory_history():
    """Returns the list of stored memories."""
    return st.session_state.internal_memory