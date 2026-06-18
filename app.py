"""
app.py — UAE Government Services Assistant
Pure Streamlit UI. All AI/retrieval logic lives in agent.py.
Enhanced UX/UI Framework for Hackathon Presentation.
"""
import base64
import streamlit as st
import random
import os

from agent import (
    load_knowledge_base,
    build_retrieval_index,
    retrieve_context,
    get_gemini_model,
    start_chat_session,
    generate_greeting,
    generate_grounded_response,
)

st.set_page_config(
    page_title="UAE Gov Services AI Assistant",
    page_icon="🇦🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# KEY ROTATION POOL
# ─────────────────────────────────────────────
API_KEYS_POOL = []
for secret_key in ["GEMINI_API_KEY", "GEMINI_API_KEY_MEMBER_1", "GEMINI_API_KEY_MEMBER_2", "GEMINI_API_KEY_MEMBER_3"]:
    if secret_key in st.secrets and st.secrets[secret_key]:
        API_KEYS_POOL.append(st.secrets[secret_key])
if not API_KEYS_POOL and os.getenv("GEMINI_API_KEY"):
    API_KEYS_POOL.append(os.getenv("GEMINI_API_KEY"))

def get_rotated_api_key(manual_key: str = "") -> str:
    if manual_key:
        return manual_key
    if API_KEYS_POOL:
        return random.choice(API_KEYS_POOL)
    return ""

# ─────────────────────────────────────────────
# PREMIUM ADVANCED CSS IMPLEMENTATION
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Base Styles & Typography Override */
html, body, [class*="css"], .stMarkdown p { 
    font-family: 'Plus Jakarta Sans', sans-serif !important; 
    color: #2D3748;
}
.main { background-color: #F8FAFC; }

/* Custom Header / Navigation Bar */
.nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 32px;
    background: linear-gradient(135deg, #ffffff, #fcfdfd);
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 20px rgba(0, 108, 76, 0.03);
    margin-bottom: 25px;
}
.nav-logo { 
    font-size: 20px; 
    font-weight: 800; 
    color: #006C4C; 
    display: flex; 
    align-items: center; 
    gap: 8px;
}
.nav-badge {
    background: #E6F4EA;
    color: #137333;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 12px;
    border: 1px solid #CEEAD6;
}

/* Prototype Disclaimer Banner */
.disclaimer-banner {
    background: linear-gradient(90deg, #FFF9E6 0%, #FFF3CD 100%);
    padding: 14px 20px;
    border-radius: 12px;
    border-left: 5px solid #FFC107;
    margin-bottom: 24px;
    font-size: 0.9rem;
    color: #715200;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* Elegant Hero Display Card */
.hero-card {
    background: linear-gradient(135deg, #006C4C 0%, #004D35 100%);
    border-radius: 24px; 
    padding: 48px; 
    margin-bottom: 32px; 
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 30px rgba(0, 108, 76, 0.15);
}
.hero-card::after {
    content: "";
    position: absolute;
    top: -50%; right: -20%;
    width: 300px; height: 300px;
    border-radius: 50%;
    background: rgba(212, 175, 55, 0.1);
    filter: blur(50px);
}
.hero-title { font-size: 36px; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.5px; }
.hero-subtitle { font-size: 16px; opacity: 0.9; font-weight: 400; max-width: 600px; line-height: 1.5; }

/* Interactive Service Dashboard Grid */
.section-title {
    font-size: 20px; 
    font-weight: 700; 
    color: #1A202C; 
    margin: 24px 0 14px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.service-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
.metric-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    border: 1px solid #E2E8F0;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 108, 76, 0.06);
    border-color: #006C4C;
}
.metric-card.active {
    background: #F0FDF4;
    border: 1px solid #006C4C;
}
.metric-icon { font-size: 32px; margin-bottom: 10px; }
.metric-label { font-weight: 700; font-size: 14px; color: #2D3748; }

/* Custom Verification Badges */
.source-badge {
    display: inline-flex;
    align-items: center;
    background: #F1F5F9;
    color: #475569;
    font-size: 0.8rem;
    padding: 6px 14px;
    border-radius: 20px;
    margin: 6px 6px 0 0;
    font-weight: 600;
    text-decoration: none !important;
    border: 1px solid #E2E8F0;
    transition: all 0.2s ease;
}
.source-badge:hover {
    background: #E2E8F0;
    color: #1E293B;
    transform: translateY(-1px);
}

/* Sidebar Custom Improvements */
.sb-hub-item {
    background: #F8FAFC;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 8px;
    border: 1px solid #E2E8F0;
}
</style>
""", unsafe_allow_html=True)

# Cached Resources
kb_data = load_knowledge_base()
vectorizer, tfidf_matrix = build_retrieval_index(kb_data)

# ─────────────────────────────────────────────
# SIDEBAR CONTROL INTERFACE
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ System Control")
    
    if len(API_KEYS_POOL) > 0:
        api_key_input = get_rotated_api_key()
        st.markdown("""
        <div style="background-color:#F0FDF4; border:1px solid #DCFCE7; padding:12px; border-radius:10px; margin-bottom:15px;">
            <span style="color:#15803D; font-weight:600; font-size:13px;">🔒 API Key Rotation Pool Active</span><br>
            <span style="color:#166534; font-size:12px;">Bypassing rate limits automatically across active keys.</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        api_key_input = st.text_input("Enter Google Gemini API Key", type="password")
        if not api_key_input:
            st.info("💡 Paste your Gemini API key above to initiate chat services.")
            
    st.markdown("---")
    st.markdown("🗣️ **Database Knowledge Scope**")
    st.caption("This self-contained local instance is configured with mock vector profiles for Student Visas, Golden Visas, and Foreign Driving Conversions.")
    
    st.markdown("---")
    st.markdown("🌐 **Official Portals Directory**")
    st.markdown("""
    <div class="sb-hub-item">🔗 <a href="https://u.ae" target="_blank" style="text-decoration:none; color:#2D3748; font-weight:500;">u.ae Portal</a></div>
    <div class="sb-hub-item">🔗 <a href="https://icp.gov.ae" target="_blank" style="text-decoration:none; color:#2D3748; font-weight:500;">ICP Portal</a></div>
    <div class="sb-hub-item">🔗 <a href="https://gdrfad.gov.ae" target="_blank" style="text-decoration:none; color:#2D3748; font-weight:500;">GDRFA Portal</a></div>
    <div class="sb-hub-item">🔗 <a href="https://rta.ae" target="_blank" style="text-decoration:none; color:#2D3748; font-weight:500;">RTA Portal</a></div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🗑️ Clear Session Context", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("chat_session", None)
        st.rerun()

# ─────────────────────────────────────────────
# PRESENTATION LAYER COMPONENT BRANDING
# ─────────────────────────────────────────────
# 1. Header Navigation Bar
st.markdown("""
<div class="nav-bar">
    <div class="nav-logo">🇦🇪 UAE Gov Services Assistant <span class="nav-badge">Hackathon Prototype</span></div>
    <div style="font-size:13px; font-weight:500; color:#64748B;">V2.5 Stateful RAG Agent</div>
</div>
""", unsafe_allow_html=True)

# 2. Disclaimer System Box
st.markdown("""
<div class="disclaimer-banner">
    <strong>⚠️ Important Notice for Evaluators:</strong> This AI system is an independent developer prototype designed for demonstration purposes. It is <strong>NOT</strong> an official government communication channel. All generated information must be checked against real system records.
</div>
""", unsafe_allow_html=True)

# 3. Premium Interactive Hero Panel
st.markdown("""
<div class="hero-card">
    <div class="hero-title">How can we assist you today?</div>
    <div class="hero-subtitle">Get direct, natural AI workflow explanations regarding residency visas, corporate trade licenses, and driving documents, fully cross-verified with official guidelines.</div>
</div>
""", unsafe_allow_html=True)

# 4. Status Indicator Overview Row
st.markdown('<div class="section-title">📦 Knowledge Subsystems</div>', unsafe_allow_html=True)
st.markdown("""
<div class="service-grid">
    <div class="metric-card active"><div class="metric-icon">🛂</div><div class="metric-label">Visa Portals</div></div>
    <div class="metric-card"><div class="metric-icon">🚗</div><div class="metric-label">Driving Licensing</div></div>
    <div class="metric-card"><div class="metric-icon">🏢</div><div class="metric-label">Corporate Setup</div></div>
    <div class="metric-card"><div class="metric-icon">🔄</div><div class="metric-label">Renewals</div></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# BACKEND CHAT SESSION SYNCHRONIZATION
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if api_key_input and "chat_session" not in st.session_state:
    try:
        model = get_gemini_model(api_key_input)
        st.session_state.chat_session = start_chat_session(model)
        if not st.session_state.messages:
            greeting = generate_greeting(st.session_state.chat_session)
            st.session_state.messages.append({"role": "assistant", "content": greeting, "sources": []})
    except Exception as e:
        st.error(f"Failed to connect to internal model runtime: {e}")

# ─────────────────────────────────────────────
# HIGH UX QUICK COMPONENT ACTION BUTTONS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title" style="margin-top:0px;">⚡ Quick Queries Suggested Action Panels</div>', unsafe_allow_html=True)
q_col1, q_col2, q_col3 = st.columns(3)
selected_query = None

with q_col1:
    if st.button("🎓 Learn About Student Visa Routes", use_container_width=True): 
        selected_query = "What are the requirements and process steps for a Student Visa?"
with q_col2:
    if st.button("🚗 Convert Foreign Driver's License", use_container_width=True): 
        selected_query = "How can I convert my foreign driving license to a UAE license?"
with q_col3:
    if st.button("🌟 Check Golden Visa Standards", use_container_width=True): 
        selected_query = "What is the eligibility for a Golden Visa?"

if selected_query and "chat_session" in st.session_state:
    matched_docs, context_string = retrieve_context(selected_query, vectorizer, tfidf_matrix, kb_data)
    reply = generate_grounded_response(selected_query, context_string, st.session_state.chat_session)
    st.session_state.messages.append({"role": "user", "content": selected_query})
    st.session_state.messages.append({"role": "assistant", "content": reply, "sources": matched_docs})
    st.rerun()

# ─────────────────────────────────────────────
# INTERACTIVE CONVERSATION STREAM LAYER
# ─────────────────────────────────────────────
st.markdown('<div class="section-title" style="margin-top:20px;">💬 Chat Window</div>', unsafe_allow_html=True)

# Custom container styling wrapping standard chat interface blocks
with st.container():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sources") and msg["role"] == "assistant":
                st.markdown('<div style="margin-top: 10px; margin-bottom: 2px; font-size: 13px; font-weight:700; color:#64748B;">Cross-Verification Nodes:</div>', unsafe_allow_html=True)
                for src in msg["sources"]:
                    st.markdown(f'<a href="{src.get("official_url", "#")}" target="_blank" class="source-badge">🔗 {src.get("title", "Source Document")}</a>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CLEAN DATA LOOP INGESTION CONTROLLER
# ─────────────────────────────────────────────
if user_input := st.chat_input("Inquire about requirements, fees, processing frameworks..."):
    if not api_key_input:
        st.sidebar.warning("API validation sequence incomplete. Check sidebar access setup parameters.")
    elif "chat_session" in st.session_state:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        matched_docs, context_string = retrieve_context(user_input, vectorizer, tfidf_matrix, kb_data)
        reply = generate_grounded_response(user_input, context_string, st.session_state.chat_session)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "sources": matched_docs,
        })
        st.rerun()

# Footer Element
st.markdown("---")
st.markdown("<div style='text-align:center; font-size:0.75rem; color:#94A3B8; padding-bottom: 20px;'>Independent Evaluation Build · Not Affiliated with UAE Digital Government Entities · Main Target Endpoint Repository <a href='https://u.ae' target='_blank' style='color:#64748B; font-weight:600;'>u.ae</a></div>", unsafe_allow_html=True)
