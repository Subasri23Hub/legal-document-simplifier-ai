import streamlit as st
from main import analyze_document, chat_with_bot
from login_ui import render_auth_gate
from auth import load_chat_history, save_chat_history, clear_chat_history

# ── Page config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="LexSimply — Legal Document Simplifier",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth gate — stop here if not logged in ───────────────────────────────────
if not render_auth_gate():
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
#  AUTHENTICATED AREA — everything below only runs when logged in
# ════════════════════════════════════════════════════════════════════════════

# ── App-specific CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }

    .header-banner {
        background: linear-gradient(135deg, #1a1f36 0%, #2d3561 100%);
        padding: 1.4rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.2rem;
        border: 1px solid #3d4a8a;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-left h1 { color: #e8c97a; font-size: 1.8rem; margin: 0; font-weight: 900; }
    .header-left p  { color: #718096; margin: 0.2rem 0 0 0; font-size: 0.85rem; }
    .header-right   { color: #a0aec0; font-size: 0.82rem; text-align: right; line-height: 1.7; }
    .header-right span { color: #e8c97a; font-weight: 700; }

    .user-bubble {
        background: #2d3561;
        border-radius: 16px 16px 4px 16px;
        padding: 0.9rem 1.2rem;
        margin: 0.5rem 0;
        color: #e2e8f0;
        border-left: 3px solid #e8c97a;
    }
    .bot-bubble {
        background: #1a2035;
        border-radius: 16px 16px 16px 4px;
        padding: 0.9rem 1.2rem;
        margin: 0.5rem 0;
        color: #e2e8f0;
        border-left: 3px solid #4a90d9;
    }
    .role-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
    }
    .user-label { color: #e8c97a; }
    .bot-label  { color: #4a90d9; }

    .info-card {
        background: #161b2e;
        border: 1px solid #2b355f;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .info-card-title {
        color: #e8c97a;
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }
    .info-card-body {
        color: #a0aec0;
        font-size: 0.84rem;
        line-height: 1.6;
    }

    .disclaimer {
        background: #1a1a2e;
        border: 1px solid #e8c97a44;
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        font-size: 0.76rem;
        color: #718096;
        margin-top: 0.8rem;
    }

    section[data-testid="stSidebar"] {
        background: #0d1021 !important;
    }

    div[data-testid="stButton"] > button {
        background: #2d3561;
        color: #e8c97a;
        border: 1px solid #3d4a8a;
        border-radius: 8px;
        font-weight: 600;
    }
    div[data-testid="stButton"] > button:hover {
        background: #3d4a8a;
        color: white;
    }

    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #4a5568;
    }
    .empty-state .icon { font-size: 3rem; }
    .empty-state h3 {
        color: #a0aec0;
        margin: 0.5rem 0;
    }
    .empty-state p {
        color: #718096;
        font-size: 0.9rem;
    }

    /* Sidebar open/close button visibility */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 999999 !important;
    }

    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    button[kind="header"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        align-items: center !important;
        justify-content: center !important;
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        min-height: 42px !important;
        background: #1a2035 !important;
        color: #e8c97a !important;
        border: 1px solid #3d4a8a !important;
        border-radius: 10px !important;
        box-shadow: 0 0 0 1px rgba(232, 201, 122, 0.15), 0 6px 18px rgba(0,0,0,0.35) !important;
        z-index: 999999 !important;
    }

    [data-testid="collapsedControl"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover,
    button[kind="header"]:hover {
        background: #2d3561 !important;
        color: #ffffff !important;
        border-color: #e8c97a !important;
    }

    /* Prevent header/banner from covering the reopen arrow */
    .block-container {
        padding-top: 4.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Load this user's persisted chat history into session ─────────────────────
user     = st.session_state.user
username = user["username"]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history(username)
if "doc_analyzed" not in st.session_state:
    st.session_state.doc_analyzed = False

# ── Header ────────────────────────────────────────────────────────────────────
display_name = user.get("full_name") or username
last_login   = user.get("last_login", "")[:16].replace("T", " ") if user.get("last_login") else "First visit"

st.markdown(f"""
<div class="header-banner">
    <div class="header-left">
        <h1>⚖️ LexSimply</h1>
        <p>Legal Document Simplifier — Secure &amp; Private</p>
    </div>
    <div class="header-right">
        👤 Signed in as <span>{display_name}</span><br/>
        🕐 Last login: {last_login}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👋 Hello, {display_name}!")
    st.markdown(f"`@{username}`")
    st.markdown("---")

    st.markdown("### 📂 Upload Legal Document")
    st.markdown("Supports **PDF**, **DOCX**, **TXT**")

    uploaded_file = st.file_uploader(
        label="Upload file",
        type=["pdf", "docx", "doc", "txt"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        st.success(f"✅ **{uploaded_file.name}** ready")
        if st.button("🔍 Analyze Document", use_container_width=True):
            with st.spinner("Reading and analyzing document..."):
                file_bytes = uploaded_file.read()
                result = analyze_document(
                    file_bytes,
                    uploaded_file.name,
                    st.session_state.chat_history,
                )
            st.session_state.chat_history.append({
                "role": "user",
                "content": f"[Uploaded: {uploaded_file.name}] Please analyze it.",
            })
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result,
            })
            save_chat_history(username, st.session_state.chat_history)
            st.session_state.doc_analyzed = True
            st.rerun()

    st.markdown("---")
    st.markdown("### 💬 Chat Tips")
    st.markdown("""
- *"What are my obligations?"*
- *"Explain clause 5 simply"*
- *"Is this safe to sign?"*
- *"What if I breach this?"*
- *"Summarize in 3 bullet points"*
""")

    st.markdown("---")
    msg_count = len(st.session_state.chat_history)
    st.markdown(f"📊 **{msg_count} messages** in your history")

    if st.button("Clear My Chat History", use_container_width=True):
        clear_chat_history(username)
        st.session_state.chat_history = []
        st.session_state.doc_analyzed = False
        st.rerun()

    if st.button("🚪 Sign Out", use_container_width=True):
        save_chat_history(username, st.session_state.chat_history)
        for key in ["logged_in", "user", "chat_history", "doc_analyzed", "auth_page"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.markdown("""
<div class="disclaimer">
    ⚠️ <strong>Disclaimer:</strong> LexSimply provides simplified explanations only.
    This is NOT legal advice. Always consult a licensed lawyer before signing.
</div>
""", unsafe_allow_html=True)

# ── Main chat area ────────────────────────────────────────────────────────────
col_chat, col_info = st.columns([3, 1])

with col_chat:
    if not st.session_state.chat_history:
        st.markdown("""
<div class="empty-state">
    <div class="icon">⚖️</div>
    <h3>Welcome to LexSimply</h3>
    <p>Upload a legal document from the sidebar<br/>
    or type your legal question below.<br/>
    Your chat history is saved privately to your account.</p>
</div>
""", unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
<div class="user-bubble">
    <div class="role-label user-label">👤 You</div>
    {msg["content"]}
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div class="bot-bubble">
    <div class="role-label bot-label">⚖️ LexSimply</div>
    {msg["content"]}
</div>""", unsafe_allow_html=True)

with col_info:
    if st.session_state.doc_analyzed:
        st.markdown("""
<div class="info-card">
    <div class="info-card-title">📋 Document Loaded</div>
    <div class="info-card-body">Ask follow-up questions about the analyzed document.</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div class="info-card">
    <div class="info-card-title">🔍 What I Analyze</div>
    <div class="info-card-body">
        📄 Document Summary<br/>
        🔑 Key Clauses<br/>
        ⚠️ Risk Areas<br/>
        📚 Legal Jargon<br/>
        ✅ Action Points
    </div>
</div>
<div class="info-card">
    <div class="info-card-title">🔐 Your Privacy</div>
    <div class="info-card-body">
        Chat history saved privately<br/>
        to your account only.<br/>
        No other user can access<br/>
        your documents or chats.
    </div>
</div>""", unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about your document or any legal question...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("LexSimply is thinking..."):
        response = chat_with_bot(user_input, st.session_state.chat_history[:-1])

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    save_chat_history(username, st.session_state.chat_history)
    st.rerun()