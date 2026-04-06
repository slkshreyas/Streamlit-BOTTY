# auth.py
import streamlit as st
import hashlib
from config.settings import Settings   # ← was missing this import

settings = Settings()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_credentials(username: str, password: str) -> bool:
    users_raw = settings.APP_USERS
    for pair in users_raw.split(","):
        pair = pair.strip()
        if ":" in pair:
            u, p = pair.split(":", 1)
            if u.strip() == username and hash_password(p.strip()) == hash_password(password):
                return True
    return False


def show_login_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background: #0a0a0f !important;
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse 80% 60% at 50% -10%, rgba(99,102,241,0.25) 0%, transparent 70%),
            radial-gradient(ellipse 50% 40% at 80% 80%, rgba(168,85,247,0.15) 0%, transparent 60%),
            #0a0a0f !important;
        min-height: 100vh;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] { display: none; }

    .login-wrap {
        max-width: 420px;
        margin: 8vh auto 0;
        padding: 48px 40px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 24px;
        backdrop-filter: blur(20px);
        box-shadow: 0 32px 80px rgba(0,0,0,0.5);
    }
    .login-logo {
        font-family: 'Syne', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #a78bfa, #60a5fa, #f0abfc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .login-sub {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.4);
        text-align: center;
        margin-bottom: 36px;
    }
    .login-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 6px;
    }
    [data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        font-family: 'DM Sans', sans-serif !important;
        padding: 12px 16px !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: rgba(167,139,250,0.6) !important;
        box-shadow: 0 0 0 3px rgba(167,139,250,0.15) !important;
    }
    [data-testid="stButton"] > button {
        width: 100% !important;
        background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        margin-top: 8px !important;
        box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
    }
    .error-msg {
        background: rgba(239,68,68,0.12);
        border: 1px solid rgba(239,68,68,0.3);
        border-radius: 10px;
        padding: 10px 14px;
        color: #fca5a5;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-logo">🤖 ConvoPro</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Powered by Gemini AI · Secure Access</div>', unsafe_allow_html=True)

    st.markdown('<div class="login-label">Username</div>', unsafe_allow_html=True)
    username = st.text_input("Username", placeholder="Enter username", label_visibility="collapsed")

    st.markdown('<div class="login-label" style="margin-top:16px">Password</div>', unsafe_allow_html=True)
    password = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="collapsed")

    if st.button("Sign In →"):
        if check_credentials(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.markdown('<div class="error-msg">❌ Invalid username or password</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def require_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        show_login_page()
        st.stop()