"""
app.py — UAE Government Services Assistant
Pure Streamlit UI. All AI/retrieval logic lives in agent.py.
"""
import base64
import streamlit as st
import random  # Added for key rotation
import os      # Added for key extraction

# ── Import everything from the agent layer ──────────────────
from agent import (
    load_knowledge_base,
    build_retrieval_index,
    retrieve_context,
    get_gemini_model,
    start_chat_session,
    generate_greeting,
    generate_grounded_response,
)
if "lang" not in st.session_state:
    st.session_state.lang = "English"

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="UAE Gov Services AI Assistant",
    page_icon="🇦🇪",
    layout="wide",
)

# ─────────────────────────────────────────────
# FREE-TIER RATE LIMIT RESILIENCE & KEY ROTATION SETUP
# ─────────────────────────────────────────────
# Gathers all team keys from Secrets to share limits and bypass 429 rate limit exceptions
API_KEYS_POOL = []
for secret_key in ["GEMINI_API_KEY", "GEMINI_API_KEY_MEMBER_1", "GEMINI_API_KEY_MEMBER_2", "GEMINI_API_KEY_MEMBER_3"]:
    if secret_key in st.secrets and st.secrets[secret_key]:
        API_KEYS_POOL.append(st.secrets[secret_key])
if not API_KEYS_POOL and os.getenv("GEMINI_API_KEY"):
    API_KEYS_POOL.append(os.getenv("GEMINI_API_KEY"))

def get_rotated_api_key(manual_key: str = "") -> str:
    """Returns a random key from the active keys pool, falling back to manual input."""
    if manual_key:
        return manual_key
    if API_KEYS_POOL:
        return random.choice(API_KEYS_POOL)
    return ""

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background-color: #F7F9FA; }
.nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 30px;
    background: white;
    border-radius: 18px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 25px;
}
.nav-logo { font-size: 22px; font-weight: 700; color: #006C4C; }
.nav-links { display: flex; gap: 28px; font-weight: 500; color: #1E293B; font-size: 14px; }
.service-card {
    background: white;
    border-radius: 18px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    border: 2px solid #E5E7EB;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.service-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
.service-card.active { background: #FFF7E6; border-color: #D4AF37; }
.service-card .icon { font-size: 30px; margin-bottom: 8px; }
.service-card .label { font-weight: 700; font-size: 14px; color: #1E293B; }
.disclaimer {
    background: #fff3cd;
    padding: 12px 18px;
    border-radius: 8px;
    border-left: 6px solid #ffc107;
    margin-bottom: 22px;
    font-size: 0.86rem;
    color: #856404;
}
.source-badge {
    display: inline-block;
    background: #e8f5e9;
    color: #2e7d32;
    font-size: 0.76rem;
    padding: 3px 10px;
    border-radius: 20px;
    margin: 3px 4px 3px 0;
    font-weight: 500;
}


</style>
""", unsafe_allow_html=True)

if st.session_state.lang == "Arabic":
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)
# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def img_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
# ─────────────────────────────────────────────
# AGENT RESOURCES  (cached at app level)
# ─────────────────────────────────────────────
@st.cache_data
def _load_kb():
    return load_knowledge_base()
@st.cache_resource
def _build_index(_data):
    return build_retrieval_index(_data)
@st.cache_resource
def _get_model(api_key: str):
    return get_gemini_model(api_key)
kb_data = _load_kb()
vectorizer, tfidf_matrix = _build_index(kb_data)
# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("🔑 Configuration")
    
    # Render active key rotation status if keys exist, or fallback to text input
    if len(API_KEYS_POOL) > 0:
        api_key_input = get_rotated_api_key()
        st.success(f"🔒 Rotation Pool: {len(API_KEYS_POOL)} free keys loaded.")
    else:
        api_key_input = st.text_input(
            "Enter Google Gemini API Key",
            type="password",
            help="Free-tier key from Google AI Studio.",
        )
        if not api_key_input:
            st.info("💡 Paste your Gemini API key above to begin.")
            
    st.markdown("---")
    st.markdown("### Trusted Verification Hubs")
    st.markdown("- [Official UAE Portal](https://u.ae)")
    st.markdown("- [ICP Portal](https://icp.gov.ae)")
    st.markdown("- [GDRFA Portal](https://gdrfad.gov.ae)")
    st.markdown("- [RTA Portal](https://rta.ae)")
    st.markdown("- [MOHRE Portal](https://mohre.gov.ae)")
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.pop("chat_session", None)
        st.rerun()

#NAVBAR
nav_col, toggle_col = st.columns([11, 1])

with toggle_col:
    if st.button("🌐 العربية" if st.session_state.lang == "English" else "🌐 English"):
        st.session_state.lang = "Arabic" if st.session_state.lang == "English" else "English"
        st.rerun()

with nav_col:
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-logo">🇦🇪 UAE Gov Assistant</div>
        <div class="nav-links">
            <span>Home</span>
            <span>Visa Services</span>
            <span>Driving License</span>
            <span>Business License</span>
            <span>About</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
# ─────────────────────────────────────────────
# DISCLAIMER BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Prototype Disclaimer:</strong>
    This application is an independent prototype built for demonstration purposes.
    It is <strong>NOT</strong> an official government portal.
    Always confirm details at the official source links provided.
</div>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
try:
    hero_enc = img_to_b64("hero_banner2.png")
    st.markdown(f"""
    <div style="position:relative; width:100%; border-radius:25px; overflow:hidden; margin-bottom:28px;">
        <img src="data:image/png;base64,{hero_enc}" style="width:100%; border-radius:25px;">
        <div style="position:absolute; top:18%; left:6%; color:black; max-width:60%;">
            <div style="font-size:42px; font-weight:800; line-height:1.05; margin-bottom:10px;">
                UAE Government<br>Services Assistant
            </div>
            <div style="font-size:18px; font-weight:500; line-height:1.3; color:#111;">
                AI-Powered Guidance for Visas, Licenses,<br>and Government Services
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#006C4C,#004d35);
                border-radius:25px; padding:50px 40px; margin-bottom:28px; color:white;">
        <div style="font-size:38px; font-weight:800; margin-bottom:10px;">
            🇦🇪 UAE Government Services Assistant
        </div>
        <div style="font-size:17px; opacity:0.9;">
            AI-Powered Guidance for Visas, Licenses, and Government Services
        </div>
    </div>
    """, unsafe_allow_html=True)
# ─────────────────────────────────────────────
# QUICK SERVICE CARDS
# ─────────────────────────────────────────────
st.markdown("<div style='font-size:22px; font-weight:700; color:#1E293B; margin-bottom:14px;'>Quick Services</div>",
            unsafe_allow_html=True)
services = [
    ("🛂", "Visa Services",    True),
    ("🚗", "Driving License",  False),
    ("🏢", "Business License", False),
    ("🔄", "Renewals",         False),
    ("❓", "FAQs",             False),
]
cols = st.columns(len(services))
for col, (icon, label, active) in zip(cols, services):
    with col:
        card_class = "service-card active" if active else "service-card"
        st.markdown(f"""
        <div class="{card_class}">
            <div class="icon">{icon}</div>
            <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if api_key_input and "chat_session" not in st.session_state:
    model = _get_model(api_key_input)
    st.session_state.chat_session = start_chat_session(model)
# Auto-greeting on first open
if not st.session_state.messages and api_key_input:
    greeting = generate_greeting(st.session_state.chat_session)
    st.session_state.messages.append({"role": "assistant", "content": greeting, "sources": []})
# ─────────────────────────────────────────────
# QUICK QUERY BUTTONS
# ─────────────────────────────────────────────
st.markdown("### ⚡ Quick Queries")
q_col1, q_col2, q_col3 = st.columns(3)
quick_query = None
with q_col1:
    if st.button("🎓 Student Visa Info"):
        quick_query = "What are the requirements and process steps for a Student Visa?"
with q_col2:
    if st.button("🚗 Convert Driving License"):
        quick_query = "How can I convert my foreign driving license to a UAE license?"
with q_col3:
    if st.button("💼 Golden Visa Options"):
        quick_query = "What is the eligibility for a Golden Visa?"
if quick_query and api_key_input:
    matched_docs, context_string = retrieve_context(quick_query, vectorizer, tfidf_matrix, kb_data)
    reply = generate_grounded_response(quick_query, context_string, st.session_state.chat_session)
    st.session_state.messages.append({"role": "user", "content": quick_query})
    st.session_state.messages.append({"role": "assistant", "content": reply, "sources": matched_docs})
    st.rerun()
# ─────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources") and msg["role"] == "assistant":
            st.markdown("**Verify on official source:**")
            for src in msg["sources"]:
                st.markdown(
                    f'<a href="{src["official_url"]}" target="_blank" class="source-badge">'
                    f'📎 {src["title"]}</a>',
                    unsafe_allow_html=True,
                )
# ─────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────
if user_input := st.chat_input("Ask about UAE visas, driving renewals, or business licenses..."):
    if not api_key_input:
        st.warning("Please enter your Gemini API key in the sidebar first.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            matched_docs, context_string = retrieve_context(
                user_input, vectorizer, tfidf_matrix, kb_data
            )
            with st.spinner("Thinking..."):
                reply = generate_grounded_response(
                    user_input, context_string, st.session_state.chat_session
                )
                st.write(reply)
                if matched_docs:
                    st.markdown("**Verify on official source:**")
                    for src in matched_docs:
                        st.markdown(
                            f'<a href="{src["official_url"]}" target="_blank" class="source-badge">'
                            f'📎 {src["title"]}</a>',
                            unsafe_allow_html=True,
                        )
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "sources": matched_docs,
        })
# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size:0.78rem; color:#999;'>"
    "🏆 Hackathon Prototype · Not affiliated with any UAE government authority · "
    "Always verify at <a href='https://u.ae' target='_blank'>u.ae</a>"
    "</div>",
    unsafe_allow_html=True,
)

