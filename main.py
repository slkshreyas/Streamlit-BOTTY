import os
import json
import hashlib
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai

# -------------------------------
# 0) Auth helpers
# -------------------------------
def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_users_from_secrets_or_env():
    """
    Priority:
      1) st.secrets["USERS"] as a JSON object: {"shreyas":"<sha256>", "admin":"<sha256>"}
      2) .env: USERNAMES (comma-separated) + PASSWORDS_SHA256 (comma-separated)
    Returns: dict {username: sha256_hash}
    """
    # 1) Try st.secrets
    try:
        if "USERS" in st.secrets:
            users_raw = st.secrets["USERS"]
            # secrets can be dict or stringified JSON; normalize to dict
            if isinstance(users_raw, str):
                users = json.loads(users_raw)
            else:
                users = dict(users_raw)
            # ensure all values are hex sha256 strings
            users = {str(u).strip(): str(p).strip() for u, p in users.items()}
            if users:
                return users
    except Exception:
        pass

    # 2) Try .env (USERNAMES + PASSWORDS_SHA256)
    usernames = os.getenv("USERNAMES", "")
    pw_hashes = os.getenv("PASSWORDS_SHA256", "")
    if usernames and pw_hashes:
        u_list = [u.strip() for u in usernames.split(",") if u.strip()]
        p_list = [p.strip() for p in pw_hashes.split(",") if p.strip()]
        if len(u_list) == len(p_list):
            return dict(zip(u_list, p_list))

    # 3) Fallback: single demo user (NOT for production)
    return {"shreyas": sha256("password123")}

def authenticate(username: str, password: str, users: dict) -> bool:
    if not username or not password:
        return False
    expected_hash = users.get(username)
    return expected_hash is not None and sha256(password) == expected_hash

def ensure_user_session_keys(username: str):
    """
    Creates per-user chat history in session_state:
    - chat_history__<username>
    - chat__<username> (Gemini chat session)
    """
    hist_key = f"chat_history__{username}"
    chat_key = f"chat__{username}"
    if hist_key not in st.session_state:
        st.session_state[hist_key] = []
    if chat_key not in st.session_state:
        st.session_state[chat_key] = None
    return hist_key, chat_key

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

# -------------------------------
# 1) Environment & API setup
# -------------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="AI Chatty", page_icon="🤖", layout="wide")

# Load users (from secrets or env)
USERS = load_users_from_secrets_or_env()

# -------------------------------
# 2) Login screen (blocks until authenticated)
# -------------------------------
def login_view():
    st.title("BOTTY🤖")
    st.subheader("Sign in")
    with st.form("login_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", value=st.session_state.get("last_username", ""))
        with col2:
            password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")

    # quick help panel
    with st.expander("Having trouble signing in?"):
        st.markdown(
            "- Ask your admin to add your credentials to **st.secrets** or `.env`.\n"
            "- For local testing, set in `.env`:\n"
            "  - `USERNAMES=shreyas`\n"
            "  - `PASSWORDS_SHA256=<sha256_of_your_password>`\n"
            "  - Use a site like CyberChef or Python to compute SHA256."
        )

    if submitted:
        st.session_state["last_username"] = username
        if authenticate(username, password, USERS):
            st.session_state["auth_user"] = username
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

if "auth_user" not in st.session_state:
    login_view()
    st.stop()

username = st.session_state["auth_user"]
hist_key, chat_key = ensure_user_session_keys(username)

# -------------------------------
# 3) Post-login: check API key
# -------------------------------
st.title("BOTTY 🤖")
st.caption(f"Signed in as **{username}**")

if not GOOGLE_API_KEY:
    st.error(
        "GOOGLE_API_KEY not found. Create a .env file with:\n\n"
        "GOOGLE_API_KEY=your_api_key_here"
    )
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# -------------------------------
# 4) Model configuration (Gemini)
# -------------------------------
# Note: You're on the legacy 'google.generativeai' SDK here, as requested.
MODEL_NAME = "gemini-3-flash-preview"  # your current selection

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction="You are a helpful assistant.",
    generation_config={
        "temperature": 1.0,
        "top_p": 1,
        "top_k": 40,
        "max_output_tokens": 2048,
    },
)

# Create (or recreate) a persistent chat session once per app run / per user
if st.session_state[chat_key] is None:
    st.session_state[chat_key] = model.start_chat(
        history=to_gemini_history(st.session_state[hist_key])
    )

# -------------------------------
# 5) Render past messages
# -------------------------------
for m in st.session_state[hist_key]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# -------------------------------
# 6) Input & response
# -------------------------------
user_prompt = st.chat_input("Ask Chatbot...")

if user_prompt:
    # Show user message
    st.session_state[hist_key].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Ask Gemini
    try:
        response = st.session_state[chat_key].send_message(user_prompt)
        assistant_response = response.text
    except Exception as e:
        assistant_response = f"⚠️ Error from Gemini API: {e}"

    # Show assistant message
    st.session_state[hist_key].append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

# -------------------------------
# 7) Sidebar controls
# -------------------------------
with st.sidebar:
    st.subheader("Settings")
