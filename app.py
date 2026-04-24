import streamlit as st
from google import genai
from PIL import Image
import datetime

# --- 1. STABLE MEMORY (Session State) ---
# This ensures your memories don't vanish when the app reruns
if "memory_bank" not in st.session_state:
    st.session_state.memory_bank = []

# --- 2. API SETUP (Secure) ---
# Note: You must add 'GOOGLE_API_KEY' to your Streamlit Secrets dashboard
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key not found! Please add GOOGLE_API_KEY to your Streamlit Secrets.")
    st.stop()

# --- 3. UI CONFIGURATION ---
st.set_page_config(page_title="AI Visual Memory Agent", page_icon="🧠", layout="centered")

st.title("🧠 AI Visual Memory Agent")
st.write("A digital extension of your spatial awareness. Record scenes and search them later.")

# --- 4. THE CAPTURE ENGINE ---
cam_input = st.camera_input("Capture a scene to remember")

if cam_input:
    # We use a button to prevent automatic API calls (saves your quota!)
    if st.button("💾 Commit to Memory"):
        img = Image.open(cam_input)
        
        # Resize for faster upload and stability
        img.thumbnail((1024, 1024))
        
        with st.spinner("Analyzing and storing in neural logs..."):
            try:
                # Using Gemini 3.1 Flash-Lite (Fastest and Most Stable for 2026 Free Tier)
                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite-preview", 
                    contents=["Describe this scene precisely for a spatial memory log. Focus on objects, text, and positions.", img]
                )
                
                # Create entry with timestamp
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                memory_entry = f"**Observation at {timestamp}:**\n{response.text}"
                
                # Save to session
                st.session_state.memory_bank.append(memory_entry)
                st.success("Memory Stored Successfully!")
                
            except Exception as e:
                st.error(f"API Error: {e}. Please wait 10 seconds and try again.")

# --- 5. THE SEARCH ENGINE (RECALL) ---
st.divider()
st.subheader("🔍 Cognitive Recall")
query = st.text_input("Ask about your history (e.g., 'Where were my keys?' or 'What shirt was I wearing?')")

if query:
    if not st.session_state.memory_bank:
        st.warning("Memory bank is empty. Save some observations first!")
    else:
        with st.spinner("Searching neural logs..."):
            # Combine all text memories into one context for the AI to read
            history_context = "\n---\n".join(st.session_state.memory_bank)
            search_prompt = f"Using the following memory logs, answer the user's question accurately. If you don't know, say so.\n\nQuestion: {query}\n\nLogs:\n{history_context}"
            
            try:
                answer = client.models.generate_content(
                    model="gemini-3.1-flash-lite-preview",
                    contents=[search_prompt]
                )
                st.chat_message("assistant").write(answer.text)
            except Exception as e:
                st.error("Recall failed. You might be hitting the rate limit.")

# --- 6. HISTORY DISPLAY ---
st.divider()
st.subheader("📜 History of Observations")
if not st.session_state.memory_bank:
    st.info("No memories logged yet.")
else:
    # Show newest memories at the top using 'reversed'
    for entry in reversed(st.session_state.memory_bank):
        with st.expander(f"Log Entry: {entry[17:36]}"): # Shows timestamp in title
            st.write(entry)