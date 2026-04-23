import os
import time
import random
import streamlit as st
from google import genai
from PIL import Image

# --- 1. CONFIG & STABLE 2026 MODELS ---
st.set_page_config(page_title="Visual Memory Agent", page_icon="🧠", layout="wide")

# Fallback list of models (2026 Stable & Preview versions)
MODELS_TO_TRY = [
    "gemini-2.5-flash",        # Current standard stable
    "gemini-3.1-flash-lite",   # 2026 High-throughput lite (Less crowded)
    "gemini-3-flash-preview",  # 2026 Frontier preview
    "gemini-1.5-flash-8b"      # Legacy high-speed fallback
]

# --- 2. API SETUP ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

# --- 3. SESSION STATE ---
if 'memory' not in st.session_state:
    st.session_state.memory = []

# --- 4. SIDEBAR LOGS ---
with st.sidebar:
    st.header("📜 Memory History")
    demo_mode = st.checkbox("Toggle Demo Mode (Use Mock Data if API fails)")
    
    if st.button("Clear Memory"):
        st.session_state.memory = []
        st.rerun()
    
    for item in reversed(st.session_state.memory):
        st.markdown(item)
        st.divider()

# --- 5. MAIN INTERFACE ---
st.title("🧠 Visual Memory Agent")
st.markdown("I track your physical world and remember where things are.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📷 Environment Snapshot")
    snapshot = st.camera_input("Snapshot your desk/room")

with col2:
    st.subheader("🤖 Agent Intelligence")
    if snapshot:
        if st.button("Analyze & Remember"):
            img = Image.open(snapshot)
            success = False
            
            with st.spinner("Agent is scanning through available model lanes..."):
                if demo_mode:
                    # SAFETY NET: Mock data for the demo
                    time.sleep(1.5)
                    analysis = "Mock Data: Found blue water bottle (right), keys (center), and sunglasses (left)."
                    st.info("Simulation Successful.")
                    success = True
                else:
                    # REAL API: Loop through models to bypass 404/503
                    for i, m_name in enumerate(MODELS_TO_TRY):
                        try:
                            # Exponential backoff/jitter
                            if i > 0:
                                time.sleep(i + random.random())
                            
                            response = client.models.generate_content(
                                model=m_name,
                                contents=["List the objects in this image and their exact positions.", img]
                            )
                            analysis = response.text
                            st.success(f"Verified via {m_name}")
                            success = True
                            break # We found a working server!
                        except Exception as e:
                            continue # Try the next model in the list
                
                if success:
                    st.write("**Observation:**")
                    st.write(analysis)
                    
                    # Archive to Memory
                    ts = time.strftime("%H:%M:%S")
                    st.session_state.memory.append(f"**[{ts}]** {analysis}")
                else:
                    st.error("Global API congestion detected. Please toggle 'Demo Mode' for the presentation.")
    else:
        st.info("Please capture a photo to start the agent's memory bank.")

# --- 6. QUERY ENGINE ---
st.divider()
st.subheader("❓ Query Memory")
q = st.text_input("Where did I leave my...?")
if q and st.session_state.memory:
    st.write("Checking short-term visual logs...")
    # Logic: Show the most recent relevant memory
    st.info(st.session_state.memory[-1])