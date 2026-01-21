# improvements needed are streaming responses , adding conversation memory aswell , and then also adding more security


import streamlit as st
import requests
import time





BACKEND_STREAM_URL = "http://127.0.0.1:8000/chat/stream"

BACKEND_URL = "http://127.0.0.1:8000/chat"

# def call_backend(prompt: str) -> str:
#     try:
#         response = requests.post(
#             BACKEND_URL,
#             json={"prompt": prompt},
#             timeout=30
#         )

#         if response.status_code == 200:
#             return response.json()["response"]
#         elif response.status_code == 429:
#             return "You're sending messages too fast. Please slow down."
#         else:
#             return "Something went wrong. Please try again."

#     except requests.exceptions.RequestException:
#         return "Unable to reach the server. Is the backend running?"






def stream_from_backend(prompt: str):
    response = requests.post(
        BACKEND_STREAM_URL,
        json={"prompt": prompt},
        stream=True,
        timeout=60
    )

    for chunk in response.iter_content(chunk_size=None):
        if chunk:
            yield chunk.decode("utf-8")









# --- 1. Page Configuration ---
# This sets the title of the browser tab and the layout.
st.set_page_config(page_title="Customer Support Chatbot", page_icon="✨", layout="wide")

# --- 2. Custom CSS (Gradient + Transparent Footer + White Pill Input) ---
page_bg_img = """
<style>
/* 1. The Main Gradient Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #FFFFFF 0%, #E5D4F5 100%);
    background-attachment: fixed;
}

/* 2. Remove the White Footer Background */
[data-testid="stBottom"] {
    background-color: transparent !important;
}
[data-testid="stBottom"] > div {
    background-color: transparent !important;
}

/* 3. The Input Wrapper (The White Pill) */
/* We style the CONTAINER, not just the text box, so the button is inside the white area */
[data-testid="stChatInput"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #B0B0B0 !important;
    border-radius: 10px !important; /* More rounded to match the design */
    color: #333333 !important;
    align-items: center !important;
}

/* 4. The Text Area (Make transparent so the wrapper color shows) */
[data-testid="stChatInput"] textarea {
    background-color: #FFFFFF !important;
    border: none !important;
    box-shadow: none !important;
    color: #333333 !important;

/* THE FIX: Use plain 'padding' to add space on ALL sides */
    /* 15px top/bottom makes it tall. 10px left/right keeps text off the edge */
    padding: 15px 10px !important;
   
    /* Optional: Force a minimum height if padding isn't enough */
    min-height: 50px !important;
}

/* 5. The Send Button */
[data-testid="stChatInput"] button {
    color: #7A8A99 !important;
}

/* 6. Remove the focus glow (the blue outline when typing) */
[data-testid="stChatInput"] > div:focus-within {
    border: 1px solid #8E8E8E !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] {
    max-width: 800px; /* Limit width to 800px */
    margin: 0 auto;   /* Center it */
}


/* --- Message Bubbles & Labels --- */

/* 1. The Role Label (e.g. "ME", "OUR AI") */
.role-label {
    font-family: sans-serif;
    font-size: 12px;
    color: #666666;     /* Dark Grey text */
    margin-bottom: 5px; /* Space between label and bubble */
    text-transform: uppercase; /* Force "ME" instead of "Me" */
    font-weight: 500;
    margin-left: 5px; /* Align with the bubble */
}

/* 2. The Message Bubble */
.message-bubble {
    background-color: rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 15px 20px;
    color: #333333;
    font-family: sans-serif;
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.4);
   
    /* Strict sizing rules */
    display: inline-block;
    width: fit-content;
    max-width: 100%; /* Relative to the wrapper, not the screen */
   
    /* Strict wrapping rules */
    overflow-wrap: break-word; /* Break long urls/words only if needed */
    word-break: keep-all;      /* IMPORTANT: Keeps "Hello" whole */
}

</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)



custom_header = """
<div style="text-align: center; margin-top: 50px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24" fill="#2C2C2C">
        <path d="M12 2L14.4 7.2L20 9L14.4 10.8L12 16L9.6 10.8L4 9L9.6 7.2L12 2Z" /> <path d="M19 15L20.2 17.4L23 18L20.2 18.6L19 21L17.8 18.6L15 18L17.8 17.4L19 15Z" /> <path d="M5 16L6.2 18.4L9 19L6.2 19.6L5 22L3.8 19.6L1 19L3.8 18.4L5 16Z" /> </svg>
    <h1 style="font-family: sans-serif; font-weight: 300; font-size: 40px; color: #1E1E1E; margin-top: 10px;margin-bottom: 50px;">
        Ask our AI anything
    </h1>
</div>
"""
st.markdown(custom_header, unsafe_allow_html=True)




# --- 3. Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Helper Function to Display Custom Messages ---
def display_custom_message(role, content):
    # 1. Determine Alignment and Label
    if role == "user":
        align = "flex-end"  # Left align
        label = "ME"
        # 10% padding from left, auto margin on right pushes it left
        container_style = "justify-content: flex-end; padding-left: 10%; padding-right: 10%;"
    else:
        align = "flex-start"    # Right align
        label = "Customer Support AI"
        # 10% padding from right, auto margin on left pushes it right
        container_style = "justify-content: flex-start; padding-left: 10%; padding-right: 10%;"

    # 2. HTML Structure
    # Outer div: Controls the Left/Right alignment on the screen
    # Inner div: Holds the Label + Bubble
    # 2. HTML Structure
    # Added "width: fit-content" to the inner div. This stops the crushing!
    message_html = f"""
    <div style="display: flex; width: 100%; {container_style} margin-bottom: 10px;">
        <div style="display: flex; flex-direction: column; width: fit-content; max-width: 70%; align-items: {align};">
            <div class="role-label">{label}</div>
            <div class="message-bubble">{content}</div>
        </div>
    </div>
    """
    st.markdown(message_html, unsafe_allow_html=True)

# --- 4. Displaying History ---
# We loop through history and use our NEW custom function
for message in st.session_state.messages:
    display_custom_message(message["role"], message["content"])

# --- 5. Handling User Input ---
if prompt := st.chat_input("Ask me anything about your projects"):
   
    # A. Display User Message immediately using custom function
    display_custom_message("user", prompt)
   
    # B. Save User Message to History
    st.session_state.messages.append({"role": "user", "content": prompt})








    #response = call_backend(prompt)  # Instead of this we are using the streaming function now below






    assistant_placeholder = st.empty()
    full_response = ""

    for chunk in stream_from_backend(prompt):
        full_response += chunk
        assistant_placeholder.markdown(
            f"""
            <div style="display: flex; width: 100%; justify-content: flex-start; padding-left: 10%; padding-right: 10%;">
                <div style="display: flex; flex-direction: column; align-items: flex-start;">
                    <div class="role-label">Customer Support AI</div>
                    <div class="message-bubble">{full_response}▌</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        time.sleep(0.02)  # 20ms feels very natural

    # Save final message
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )