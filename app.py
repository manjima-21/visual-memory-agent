import streamlit as st
import PIL.Image
import time
from google.genai import types
from agent import client, MODEL_ID, save_to_memory, internal_memory

# This makes the website look nice
st.set_page_config(page_title="Memory Agent", page_icon="🧠")
st.title("🧠 Personal Memory Agent")
st.write("I help you remember where you put your things.")

# 1. THE CAMERA
# On a phone, this will open the actual camera. On a laptop, the webcam.
img_file = st.camera_input("Snapshot your desk")

if img_file:
    img = PIL.Image.open(img_file)
    
    if st.button("Analyze Scene"):
        with st.spinner("Agent is thinking..."):
            # We use the same brain logic you already built!
            prompt = "Look at this image. If you see a phone, keys, or wallet, use the 'save_to_memory' tool. Otherwise, describe the scene briefly."
            
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[prompt, img],
                config=types.GenerateContentConfig(
                    tools=[save_to_memory],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                )
            )
            st.success("Scene Processed!")
            if response.text:
                st.write(f"**Agent Thought:** {response.text}")

# 2. THE SEARCH BOX (No more 'm' key needed!)
st.divider()
st.subheader("🔍 Ask your Brain")
query = st.text_input("What are you looking for?")

if query:
    # Join all memories into one text for the AI to read
    context = "\n".join(internal_memory) if internal_memory else "No memories yet."
    
    ans = client.models.generate_content(
        model=MODEL_ID, 
        contents=f"History: {context}\nQuestion: {query}\nAnswer based on history."
    )
    st.info(f"**Agent:** {ans.text}")

# 3. THE AUDIT LOG
with st.expander("Show Memory Log"):
    for entry in internal_memory:
        st.write(entry)