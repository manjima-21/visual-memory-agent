import streamlit as st
from google import genai
from PIL import Image

# --- 1. STABLE MEMORY ---
if "memory_bank" not in st.session_state:
    st.session_state.memory_bank = []

# --- 2. API SETUP ---
client = genai.Client(api_key="AIzaSyD7gHPMKLGdVv1pbKau6Pwl3gCNR-8bb6g")

# --- 3. UI ---
st.title("🧠 AI Visual Memory Agent")
cam_input = st.camera_input("Capture a scene to remember")

if cam_input:
    # REFRESH-PROOF TRIGGER
    if st.button("💾 Save to Memory"):
        img = Image.open(cam_input)
        
        # RESIZE FOR STABILITY
        img.thumbnail((1024, 1024))
        
        with st.spinner("Analyzing and storing memory..."):
            try:
                # USE FLASH-8B FOR MAX STABILITY
                # Change this line in your app.py:
                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite-preview", # <-- Use this updated model name
                    contents=["Describe this scene for my memory log.", img]
                )
                
                # STORE IN SESSION STATE
                st.session_state.memory_bank.append(response.text)
                st.success("Memory Stored!")
            except Exception as e:
                st.error(f"API Error: {e}. Try waiting 10 seconds.")

# --- 4. DISPLAY ---
st.divider()
st.subheader("📜 History of Observations")
for entry in reversed(st.session_state.memory_bank):
    st.info(entry)