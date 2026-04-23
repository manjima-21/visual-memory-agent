import streamlit as st
from PIL import Image
from agent import analyze_scene, get_memory_history

# Page Config
st.set_page_config(page_title="Visual Memory Agent", page_icon="🧠")

st.title("🧠 Personal Memory Agent")
st.markdown("I help you remember where you put your things using AI Vision.")

# --- SIDEBAR: MEMORY LOG ---
st.sidebar.header("📜 Memory History")
history = get_memory_history()

if not history:
    st.sidebar.info("No memories logged yet. Take a snapshot!")
else:
    for item in reversed(history): # Show newest first
        st.sidebar.write(item)
        st.sidebar.divider()

# --- MAIN INTERFACE: CAMERA ---
st.subheader("Step 1: Capture your environment")
snapshot = st.camera_input("Snapshot your desk")

if snapshot:
    st.subheader("Step 2: Analyze & Remember")
    if st.button("🔍 Analyze Scene"):
        # Convert Streamlit upload to PIL Image for Gemini
        img = Image.open(snapshot)
        
        with st.spinner("Agent is scanning the scene..."):
            result = analyze_scene(img)
            
        if "Error" in result:
            st.error(result)
        else:
            st.success("Scene analyzed and saved to memory!")
            st.write("**Agent Observation:**")
            st.info(result)

# --- CHAT INTERFACE: QUERY ---
st.divider()
st.subheader("Step 3: Ask your Agent")
user_query = st.text_input("e.g., 'Where did I leave my keys?'")

if user_query:
    if not history:
        st.warning("I don't have any memories yet. Please analyze a scene first!")
    else:
        st.write("**Searching memory...**")
        # Simple logical check for the demo
        # (In a full app, you'd send the query + history to Gemini)
        st.write("Based on my logs, here is what I remember:")
        st.write(history[-1]) # Show the most recent context