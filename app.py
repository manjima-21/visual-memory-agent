import os
import time
import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Memory Agent", page_icon="🧠", layout="wide")

# API Key Handling
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.getenv("GOOGLE_API_KEY")

# Initialize the STABLE SDK
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. SESSION STATE (MEMORY) ---
if 'memory' not in st.session_state:
    st.session_state.memory = []

# --- 3. SIDEBAR (LOGS) ---
with st.sidebar:
    st.header("📜 Memory Logs")
    if not st.session_state.memory:
        st.info("No items remembered yet.")
    else:
        if st.button("Clear Brain"):
            st.session_state.memory = []
            st.rerun()
        for entry in reversed(st.session_state.memory):
            st.markdown(entry)
            st.divider()

# --- 4. MAIN UI ---
st.title("🧠 Visual Memory Agent")
st.write("Snap a photo, and I'll remember where your items are.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📷 Capture")
    snapshot = st.camera_input("Take a snapshot of your desk")

with col2:
    st.subheader("🔍 Agent Analysis")
    if snapshot:
        if st.button("Analyze & Archive"):
            img = Image.open(snapshot)
            with st.spinner("Thinking..."):
                try:
                    # The vision call
                    response = model.generate_content(["List the objects in this image and their positions.", img])
                    
                    # UI update
                    st.success("Memory Saved!")
                    st.markdown(response.text)
                    
                    # Archive in memory
                    timestamp = time.strftime("%H:%M:%S")
                    st.session_state.memory.append(f"**[{timestamp}]** {response.text}")
                    
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("Awaiting snapshot...")