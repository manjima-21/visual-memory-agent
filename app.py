import os
import time
import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Memory Agent", page_icon="🧠")

# 1. API SETUP
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

# 2. THE MULTI-MODEL FALLBACK (To fix that 404!)
# We will try these names in order until one works
MODELS_TO_TRY = ["gemini-1.5-flash", "gemini-1.5-flash-002", "gemini-2.0-flash"]

if 'internal_memory' not in st.session_state:
    st.session_state.internal_memory = []

# 3. UI
st.title("🧠 Visual Memory Agent")

with st.sidebar:
    st.header("📜 Memory History")
    for item in reversed(st.session_state.internal_memory):
        st.write(item)
        st.divider()

snapshot = st.camera_input("Take a photo")

if snapshot:
    if st.button("Analyze Scene"):
        img = Image.open(snapshot)
        success = False
        
        with st.spinner("Searching for a stable model connection..."):
            for model_name in MODELS_TO_TRY:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=["What is in this image? Be brief.", img]
                    )
                    # If we reach here, it worked!
                    analysis = response.text
                    st.success(f"Analyzed using {model_name}")
                    st.write(analysis)
                    
                    # Save to memory
                    timestamp = time.strftime("%H:%M:%S")
                    st.session_state.internal_memory.append(f"[{timestamp}] {analysis}")
                    success = True
                    break # Stop trying other models
                except Exception as e:
                    # If it's a 404, we just try the next model in the list
                    continue
            
            if not success:
                st.error("Google's servers are busy. Please try clicking again in 10 seconds.")