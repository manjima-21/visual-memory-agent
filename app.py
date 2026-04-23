import os
import time
import random
import streamlit as st
from google import genai
from PIL import Image

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Visual Memory Agent", page_icon="🧠", layout="wide")

# The "2026 Resilience List" - Using Lite and Pro models to bypass capacity errors
MODELS_TO_TRY = [
    "gemini-3.1-flash-lite-preview", # Best chance for a success response
    "gemini-3-flash-preview",       # Frontier performance
    "gemini-2.5-flash",             # Reliable backup
    "gemini-1.5-flash-8b"           # Legacy fallback
]

# API Key Handling
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.getenv("GOOGLE_API_KEY")

# Initialize the 2026 GenAI Client
client = genai.Client(api_key=api_key)

# --- 2. MEMORY STORAGE ---
if 'memory' not in st.session_state:
    st.session_state.memory = []

# --- 3. SIDEBAR (LOGS) ---
with st.sidebar:
    st.header("📜 Visual Memory Log")
    st.write("Current Session History:")
    
    if st.button("Wipe Brain"):
        st.session_state.memory = []
        st.rerun()
    
    for entry in reversed(st.session_state.memory):
        st.markdown(entry)
        st.divider()

# --- 4. MAIN APP INTERFACE ---
st.title("🧠 Visual Memory Agent")
st.write("Capture your environment. I will track your items and remember their locations.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📷 Visual Input")
    snapshot = st.camera_input("Snapshot your surroundings")

with col2:
    st.subheader("🤖 Agent Reasoning")
    if snapshot:
        if st.button("Analyze Environment"):
            img = Image.open(snapshot)
            success = False
            
            with st.spinner("🔍 AI is processing real-time visual data..."):
                # LOOP: Tries different models to beat the 503/404 errors
                for i, model_name in enumerate(MODELS_TO_TRY):
                    try:
                        # Exponential backoff: if first model fails, wait a bit before trying next
                        if i > 0:
                            time.sleep(1 + random.random())
                        
                        response = client.models.generate_content(
                            model=model_name,
                            contents=[
                                "List the objects in this image and describe their positions (e.g., 'to the left of the laptop'). Be specific.", 
                                img
                            ]
                        )
                        
                        # If successful, extract text
                        analysis = response.text
                        st.success(f"Success! Analyzed via {model_name}")
                        st.markdown(f"**Observations:**\n{analysis}")
                        
                        # Save to memory
                        ts = time.strftime("%H:%M:%S")
                        st.session_state.memory.append(f"**[{ts}]** {analysis}")
                        success = True
                        break # Exit loop on success
                        
                    except Exception as e:
                        # Silently try the next model in the list
                        continue
                
                if not success:
                    st.error("Google's local server is at capacity. Refresh and try again in 30 seconds.")
    else:
        st.info("Awaiting visual snapshot...")

# --- 5. SEARCH FEATURE ---
st.divider()
st.subheader("🔍 Query Your History")
query = st.text_input("Ask about an item (e.g., 'Where is my coffee mug?')")
if query and st.session_state.memory:
    # Basic logic: Show the most recent memory entry
    st.write("Scanning visual logs...")
    st.info(f"Most recent log: {st.session_state.memory[-1]}")