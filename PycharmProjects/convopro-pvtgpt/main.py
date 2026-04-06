import streamlit as st
from auth import require_login
from services.get_models_list import get_gemini_models_list
from services.get_title import get_chat_title
from services.chat_utilities import get_answer
from db.conversations import (
    create_new_conversation,
    add_message,
    get_conversation,
    get_all_conversations,
)

st.set_page_config(page_title="ConvoPro", page_icon="🤖", layout="centered")

# ── Auth gate ─────────────────────────────────────────────────────────────────
require_login()

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body { font-family: 'DM Sans', sans-serif; }

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 90% 50% at 50% -5%, rgba(99,102,241,0.18) 0%, transparent 65%),
        radial-gradient(ellipse 40% 35% at 90% 85%, rgba(168,85,247,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 35% 30% at 5% 95%, rgba(59,130,246,0.1) 0%, transparent 55%),
        #07070f !important;
    min-height: 100vh;
}

[data-testid="stHeader"] {
    background: rgba(7,7,15,0.8) !important;
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

[data-testid="stSidebar"] {
    background: rgba(10,10,20,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(20px);
}

[data-testid="stSidebar"] [data-testid="stButton"] > button {
    width: 100% !important;
    text-align: left !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.7) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    padding: 10px 14px !important;
    margin-bottom: 4px !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(167,139,250,0.1) !important;
    border-color: rgba(167,139,250,0.3) !important;
    color: white !important;
    transform: translateX(3px) !important;
}

h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.2rem !important;
    background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 50%, #f0abfc 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    letter-spacing: -1px !important;
}

[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: white !important;
}
[data-testid="stSelectbox"] label {
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.78rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(10px) !important;
    margin-bottom: 12px !important;
    padding: 16px !important;
}
[data-testid="stChatMessage"]:hover {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(167,139,250,0.2) !important;
}

[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
}
[data-testid="stChatInput"] textarea { color: white !important; }

[data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.85) !important;
    font-family: 'DM Sans', sans-serif !important;
    line-height: 1.7 !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(167,139,250,0.3); border-radius: 4px; }

@keyframes float1 {
    0%,100% { transform: translate(0,0); }
    33% { transform: translate(30px,-20px); }
    66% { transform: translate(-15px,15px); }
}
@keyframes float2 {
    0%,100% { transform: translate(0,0); }
    50% { transform: translate(-25px,20px); }
}
</style>
""", unsafe_allow_html=True)

# ── Floating background orbs ──────────────────────────────────────────────────
st.markdown("""
<div style="position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden">
    <div style="position:absolute;top:15%;left:10%;width:400px;height:400px;
        background:radial-gradient(circle,rgba(99,102,241,0.08) 0%,transparent 70%);
        border-radius:50%;animation:float1 12s ease-in-out infinite;"></div>
    <div style="position:absolute;bottom:20%;right:8%;width:350px;height:350px;
        background:radial-gradient(circle,rgba(168,85,247,0.07) 0%,transparent 70%);
        border-radius:50%;animation:float2 15s ease-in-out infinite;"></div>
    <div style="position:absolute;top:50%;left:50%;width:500px;height:200px;
        background:radial-gradient(ellipse,rgba(59,130,246,0.05) 0%,transparent 70%);
        border-radius:50%;transform:translate(-50%,-50%);"></div>
</div>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
username = st.session_state.get("username", "User")
col1, col2 = st.columns([5, 1])
with col1:
    st.title("🤖 ConvoPro")
with col2:
    st.markdown(f"<div style='text-align:right;padding-top:18px;font-family:DM Sans;font-size:0.8rem;color:rgba(255,255,255,0.4)'>👤 {username}</div>", unsafe_allow_html=True)
    if st.button("🚪", help="Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

# ── Models ────────────────────────────────────────────────────────────────────
if "GEMINI_MODELS" not in st.session_state:
    st.session_state.GEMINI_MODELS = get_gemini_models_list()
selected_model = st.selectbox("Select Gemini Model", st.session_state.GEMINI_MODELS)

# ── Session state ─────────────────────────────────────────────────────────────
st.session_state.setdefault("conversation_id", None)
st.session_state.setdefault("conversation_title", None)
st.session_state.setdefault("chat_history", [])

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.07)'>💬 Chat History</div>", unsafe_allow_html=True)
    conversations = get_all_conversations()

    if st.button("➕  New Chat"):
        st.session_state.conversation_id = None
        st.session_state.conversation_title = None
        st.session_state.chat_history = []

    for cid, title in conversations.items():
        is_current = cid == st.session_state.conversation_id
        label = f"● {title}" if is_current else f"○ {title}"
        if st.button(label, key=f"conv_{cid}"):
            doc = get_conversation(cid) or {}
            st.session_state.conversation_id = cid
            st.session_state.conversation_title = doc.get("title", "Untitled")
            st.session_state.chat_history = [
                {"role": m["role"], "content": m["content"]}
                for m in doc.get("messages", [])
            ]

    st.markdown("<div style='position:absolute;bottom:20px;left:0;right:0;text-align:center;font-family:DM Sans;font-size:0.7rem;color:rgba(255,255,255,0.2);padding:0 16px'>ConvoPro · Secured Access<br>Powered by Google Gemini</div>", unsafe_allow_html=True)

# ── Chat messages ─────────────────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
user_query = st.chat_input("Ask ConvoPro anything...")
if user_query:
    st.chat_message("user").markdown(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    if st.session_state.conversation_id is None:
        try:
            title = get_chat_title(selected_model, user_query) or "New Chat"
        except Exception:
            title = "New Chat"
        conv_id = create_new_conversation(title=title, role="user", content=user_query)
        st.session_state.conversation_id = conv_id
        st.session_state.conversation_title = title
    else:
        add_message(st.session_state.conversation_id, "user", user_query)

    try:
        assistant_text = get_answer(selected_model, st.session_state.chat_history)
    except Exception as e:
        assistant_text = f"[Error: {e}]"

    with st.chat_message("assistant"):
        st.markdown(assistant_text)
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})

    if st.session_state.conversation_id:
        add_message(st.session_state.conversation_id, "assistant", assistant_text)
