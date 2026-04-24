import streamlit as st
from google import genai
from PIL import Image

# --- 1. STABLE MEMORY ---
if "memory_bank" not in st.session_state:
    st.session_state.memory_bank = []

# --- 2. API SETUP ---
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

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
                response = client.models.generate_content(
                    model="gemini-1.5-flash-8b",
                    contents=["Precisely describe the objects in this image and their positions for a spatial memory log.", img]
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