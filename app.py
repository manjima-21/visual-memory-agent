import os
import time
import streamlit as st
from google import genai
from PIL import Image

# 1. PAGE SETUP
st.set_page_config(page_title="Visual Memory Agent", page_icon="🧠", layout="wide")

# 2. API KEY SETUP
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

# Initialize Client
client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-1.5-flash" 

# 3. MEMORY LOGIC
if 'internal_memory' not in st.session_state:
    st.session_state.internal_memory = []

def save_to_memory(observation: str):
    timestamp = time.strftime("%H:%M:%S")
    entry = f"**[{timestamp}]** {observation}"
    st.session_state.internal_memory.append(entry)

# 4. UI - SIDEBAR (THE LOG)
with st.sidebar:
    st.header("📜 Memory History")
    if not st.session_state.internal_memory:
        st.info("No items logged yet.")
    else:
        # Clear Memory Button
        if st.button("Clear History"):
            st.session_state.internal_memory = []
            st.rerun()
        
        for item in reversed(st.session_state.internal_memory):
            st.markdown(item)
            st.divider()

# 5. UI - MAIN PANEL
st.title("🧠 Visual Memory Agent")
st.write("Your AI-powered 'Second Brain' for tracking physical objects.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📷 Snapshot")
    snapshot = st.camera_input("Capture your desk/room")

with col2:
    st.subheader("🤖 Analysis")
    if snapshot:
        if st.button("Analyze & Remember"):
            img = Image.open(snapshot)
            with st.spinner("Processing image..."):
                try:
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=["Be concise. List the main objects in this image and their approximate locations.", img]
                    )
                    
                    # Display Result
                    st.success("Memory Captured!")
                    st.markdown(response.text)
                    
                    # Save to Session State
                    save_to_memory(response.text)
                    
                except Exception as e:
                    if "RESOURCE_EXHAUSTED" in str(e):
                        st.error("Quota exceeded. Please wait 60 seconds or use a new API key.")
                    else:
                        st.error(f"Error: {e}")
    else:
        st.info("Please take a photo to begin.")

# 6. QUERY SECTION
st.divider()
st.subheader("❓ Ask Memory")
query = st.text_input("Where did I put my...?")
if query and st.session_state.internal_memory:
    st.write("Searching through your history...")
    # For the demo, we show the last known context
    st.write("Based on the most recent scan:")
    st.info(st.session_state.internal_memory[-1])