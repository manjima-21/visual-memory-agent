import os
import time  # <--- Added this back!
import streamlit as st
from google import genai

# 1. API Key Setup
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.0-flash" 

# 2. Persist Memory in Streamlit Session State
if 'internal_memory' not in st.session_state:
    st.session_state.internal_memory = []

# Create a local reference so your other functions don't break
internal_memory = st.session_state.internal_memory

def save_to_memory(observation: str, location: str = "unknown") -> str:
    # Use time.strftime now that we've imported it
    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {observation} at {location}"
    
    # Append to the session_state version so it's saved forever
    st.session_state.internal_memory.append(entry)
    
    # This shows up in the Streamlit logs for you to see
    print(f"✨ MEMORY LOGGED: {entry}")
    return "Successfully archived in memory."