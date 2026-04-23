import cv2
import time
import PIL.Image
from google.genai import types
from agent import client, MODEL_ID, save_to_memory, internal_memory

# 1. Initialize Webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Camera not found.")
    exit()

print(f"--- Visual Agent Active ({MODEL_ID}) ---")
print("INSTRUCTIONS:")
print("1. Click the CAMERA window to use keys.")
print("2. Hold 'm' on the camera window to ask a question.")
print("3. Press 'q' on the camera window to quit.")

last_capture_time = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret: break

        # Always show the live feed
        cv2.imshow('Agent Eyes', frame)

        # Trigger vision analysis every 15 seconds
        current_time = time.time()
        if current_time - last_capture_time > 15:
            print("\n[Brain] Analyzing scene...")
            
            # Resize small to reduce "hanging" and save tokens
            small_frame = cv2.resize(frame, (320, 240)) 
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            pil_img = PIL.Image.fromarray(rgb_frame)

            prompt = """
            Look at this frame. 
            1. If the user just placed an object (phone, keys, etc.) down, use 'save_to_memory'.
            2. If the user is holding an object, log 'User is holding X'.
            3. If no change is happening, say 'Monitoring'.
            """

            # Retry loop for 503 Server Busy errors
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=[prompt, pil_img],
                        config=types.GenerateContentConfig(
                            tools=[save_to_memory],
                            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                        )
                    )
                    if response.text:
                        print(f"Agent Thought: {response.text.strip()}")
                    break 
                except Exception as e:
                    if "503" in str(e) and attempt < 2:
                        print(f"Server busy, retrying...")
                        time.sleep(2)
                    else:
                        print(f"API Error: {e}")
                        break

            last_capture_time = time.time()

        # --- KEYBOARD INTERRUPT LOGIC ---
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break

        if key == ord('m'):
            print("\n" + "="*40)
            print("  INTERRUPT: BRAIN PAUSED FOR QUERY  ")
            print("="*40)
            
            # This stops the loop until you hit Enter in the terminal
            question = input("TYPE YOUR QUESTION: ")
            
            if question.strip():
                print("[Brain] Searching Memory...")
                memory_context = "\n".join(internal_memory) if internal_memory else "No memories recorded."
                
                query_prompt = f"Memory History:\n{memory_context}\n\nQuestion: {question}\nAnswer briefly."
                
                try:
                    query_res = client.models.generate_content(model=MODEL_ID, contents=query_prompt)
                    print(f"\n✨ ANSWER: {query_res.text}")
                except Exception as e:
                    print(f"Query Error: {e}")
            
            print("\n" + "="*40)
            print("  RESUMING MONITORING...  ")
            print("="*40 + "\n")
            
            # Reset timer so it doesn't analyze immediately after you finish typing
            last_capture_time = time.time()

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("System Shutdown.")