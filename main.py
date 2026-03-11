import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai

# -------------------------------
# 1) Environment & API setup
# -------------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="AI Chatty", page_icon="🤖", layout="wide")
st.title("BOTTY")

if not GOOGLE_API_KEY:
    st.error(
        "GOOGLE_API_KEY not found. Create a .env file with:\n\nGOOGLE_API_KEY=your_api_key_here"
    )
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# -------------------------------
# 2) Model configuration (Gemini)
# -------------------------------
# Pick one of:
#   - "gemini-1.5-flash"  (faster, cheaper)
#   - "gemini-1.5-pro"    (more capable)
MODEL_NAME = "gemini-3-flash-preview"

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction="You are a helpful assistant.",
    generation_config={
        "temperature": 1.0,  # mirrors your Groq setting
        "top_p": 1,
        "top_k": 40,
        "max_output_tokens": 2048,
    },
)

# -------------------------------
# 3) State initialization
# -------------------------------
if "chat_history" not in st.session_state:
    # We'll store Streamlit-renderable history as roles: "user" | "assistant"
    st.session_state.chat_history = []

def to_gemini_history(history):
    """
    Convert Streamlit-friendly history to Gemini's expected format.
    Streamlit uses roles: 'user'/'assistant'; Gemini expects 'user'/'model'.
    """
    converted = []
    for m in history:
        role = "model" if m["role"] == "assistant" else "user"
        converted.append({"role": role, "parts": [m["content"]]})
    return converted

# Create (or recreate) a persistent chat session once per app run
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=to_gemini_history(st.session_state.chat_history))

# -------------------------------
# 4) Render past messages
# -------------------------------
for m in st.session_state.chat_history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# -------------------------------
# 5) Input & response
# -------------------------------
user_prompt = st.chat_input("Ask Chatbot...")

if user_prompt:
    # Show user message
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Ask Gemini
    try:
        response = st.session_state.chat.send_message(user_prompt)
        assistant_response = response.text
    except Exception as e:
        assistant_response = f"⚠️ Error from Gemini API: {e}"

    # Show assistant message
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

# -------------------------------
# 6) Sidebar controls
# -------------------------------
with st.sidebar:
    st.subheader("Settings")
    st.caption(f"Model: `{MODEL_NAME}`  •  Temp:10.0")
    if st.button("🧹 Clear the chat Boy"):
        st.session_state.chat_history = []
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()