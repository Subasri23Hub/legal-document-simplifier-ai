import streamlit as st
from auth import register_user, login_user


def inject_auth_css():
    st.markdown("""
<style>
    /* ── Global white background ── */
    .stApp, .stApp > div, section.main, .block-container {
        background-color: #ffffff !important;
    }

    /* ── Logo ── */
    .auth-logo {
        text-align: center;
        margin-bottom: 1.8rem;
    }
    .auth-logo .logo-icon { font-size: 3rem; display: block; margin-bottom: 0.4rem; }
    .auth-logo h1 { color: #1a56db; font-size: 2.2rem; font-weight: 900; margin: 0; }
    .auth-logo p  { color: #6b7280; font-size: 0.9rem; margin: 0.3rem 0 0 0; }

    /* ── Card ── */
    .auth-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 2.2rem 2rem;
        box-shadow: 0 4px 24px rgba(26,86,219,0.08);
    }
    .auth-card h2 { color: #111827; font-size: 1.25rem; font-weight: 700;
                    margin: 0 0 1.4rem 0; text-align: center; }

    /* ── Inputs ── */
    div[data-testid="stTextInput"] label {
        color: #374151 !important; font-size: 0.85rem !important; font-weight: 600 !important;
    }
    div[data-testid="stTextInput"] input {
        background: #f9fafb !important; color: #111827 !important;
        border: 1.5px solid #d1d5db !important; border-radius: 8px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #1a56db !important;
        box-shadow: 0 0 0 3px rgba(26,86,219,0.12) !important;
        background: #ffffff !important;
    }

    /* ── Primary button ── */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: #1a56db !important; color: #ffffff !important;
        font-weight: 700 !important; border: none !important;
        border-radius: 8px !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover { background: #1e429f !important; }

    /* ── Secondary button ── */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: #ffffff !important; color: #1a56db !important;
        border: 1.5px solid #1a56db !important; border-radius: 8px !important; font-weight: 600 !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover { background: #eff6ff !important; }

    /* ── Badge ── */
    .security-badge {
        background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px;
        padding: 0.65rem 1rem; font-size: 0.78rem; color: #1e40af;
        margin-top: 1rem; text-align: center; line-height: 1.5;
    }

    /* ── Footer ── */
    .auth-footer {
        text-align: center; color: #9ca3af; font-size: 0.76rem;
        margin-top: 1.2rem; line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)


def render_logo():
    st.markdown("""
<div class="auth-logo">
    <span class="logo-icon">⚖️</span>
    <h1>LexSimply</h1>
    <p>Legal Document Simplifier — Secure &amp; Private</p>
</div>
""", unsafe_allow_html=True)


def render_login_form():
    st.markdown('<div class="auth-card"><h2>🔐 Sign In to Your Account</h2>', unsafe_allow_html=True)
    username = st.text_input("Username", placeholder="Enter your username", key="login_username")
    password = st.text_input("Password", placeholder="Enter your password", type="password", key="login_password")
    c1, c2 = st.columns(2)
    with c1: login_btn  = st.button("Sign In", type="primary", use_container_width=True, key="btn_login")
    with c2: signup_btn = st.button("Create Account", type="secondary", use_container_width=True, key="btn_go_signup")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="security-badge">🔒 Passwords hashed with SHA-256 + salt. Never stored in plain text.</div>', unsafe_allow_html=True)

    if login_btn:
        if not username or not password:
            st.error("Please enter both username and password."); return
        success, msg, user_data = login_user(username, password)
        if success:
            st.session_state.logged_in = True
            st.session_state.user = user_data
            st.rerun()
        else:
            st.error(msg)
    if signup_btn:
        st.session_state.auth_page = "signup"; st.rerun()


def render_signup_form():
    st.markdown('<div class="auth-card"><h2>✨ Create New Account</h2>', unsafe_allow_html=True)
    full_name = st.text_input("Full Name", placeholder="e.g. Kousalya R", key="signup_name")
    username  = st.text_input("Username", placeholder="Letters, numbers, underscores", key="signup_username")
    password  = st.text_input("Password", placeholder="Minimum 6 characters", type="password", key="signup_password")
    confirm   = st.text_input("Confirm Password", placeholder="Re-enter password", type="password", key="signup_confirm")
    c1, c2 = st.columns(2)
    with c1: signup_btn = st.button("Create Account", type="primary", use_container_width=True, key="btn_signup")
    with c2: back_btn   = st.button("Back to Login", type="secondary", use_container_width=True, key="btn_back_login")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="security-badge">🛡️ Each account gets its own isolated private chat history.</div>', unsafe_allow_html=True)

    if signup_btn:
        if not username or not password or not confirm:
            st.error("Please fill in all required fields."); return
        if password != confirm:
            st.error("Passwords do not match."); return
        success, msg = register_user(username, password, full_name)
        if success:
            st.success(msg + " Please sign in.")
            st.session_state.auth_page = "login"; st.rerun()
        else:
            st.error(msg)
    if back_btn:
        st.session_state.auth_page = "login"; st.rerun()


def render_auth_gate() -> bool:
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "auth_page" not in st.session_state: st.session_state.auth_page = "login"
    if st.session_state.logged_in:
        return True

    inject_auth_css()
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        render_logo()
        if st.session_state.auth_page == "login":
            render_login_form()
        else:
            render_signup_form()
        st.markdown('<div class="auth-footer">⚠️ LexSimply provides simplified explanations only — not legal advice.<br/>Always consult a licensed lawyer before signing any document.</div>', unsafe_allow_html=True)
    return False