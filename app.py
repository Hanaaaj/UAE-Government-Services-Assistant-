"""
app.py — UAE Government Services Assistant
Pure Streamlit UI custom-tailored to a pixel-perfect design system.
"""
import base64
import streamlit as st
import random  
import os     
 
from agent import (
    UI,
    load_knowledge_base,
    build_retrieval_index,
    retrieve_context,
    get_gemini_model,
    start_chat_session,
    generate_grounded_response,
)
 
# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="UAE Gov Services AI Assistant",
    page_icon="🇦🇪",
    layout="wide",
    initial_sidebar_state="collapsed"
)
 
# ─────────────────────────────────────────────
# FREE-TIER RATE LIMIT RESILIENCE & KEY ROTATION SETUP
# ─────────────────────────────────────────────
API_KEYS_POOL = []
for secret_key in ["GEMINI_API_KEY", "GEMINI_API_KEY_MEMBER_1", "GEMINI_API_KEY_MEMBER_2", "GEMINI_API_KEY_MEMBER_3"]:
    try:
        if secret_key in st.secrets and st.secrets[secret_key]:
            API_KEYS_POOL.append(st.secrets[secret_key])
    except Exception:
        pass
if not API_KEYS_POOL and os.getenv("GEMINI_API_KEY"):
    API_KEYS_POOL.append(os.getenv("GEMINI_API_KEY"))
 
def get_rotated_api_key(manual_key: str = "") -> str:
    if manual_key:
        return manual_key
    if "active_api_key" not in st.session_state:
        st.session_state.active_api_key = random.choice(API_KEYS_POOL) if API_KEYS_POOL else ""
    return st.session_state.active_api_key
 
# ─────────────────────────────────────────────
# LANGUAGE STATE
# ─────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "English"
 
t = UI[st.session_state.lang]         
is_arabic = st.session_state.lang == "Arabic"

# ─────────────────────────────────────────────
# INITIALIZE AGENT RETRIEVAL PIPELINE SYSTEM DATA
# ─────────────────────────────────────────────
@st.cache_resource
def initialize_agent_backend():
    kb_data = load_knowledge_base()
    vectorizer, tfidf_matrix = build_retrieval_index(kb_data)
    return kb_data, vectorizer, tfidf_matrix

kb_data, vectorizer, tfidf_matrix = initialize_agent_backend()
 
# ─────────────────────────────────────────────
# ADVANCED CUSTOM CSS FOR TARGET DESIGN
# ─────────────────────────────────────────────
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700;800&family=Cairo:wght=300;400;600;700;800&display=swap');
 
/* Global Canvas Adjustments */
html, body, [class*="css"], .stApp { 
    font-family: 'Inter', sans-serif; 
    background-color: #FDFDFB !important;
}

/* Force all text inside chat messages to remain visible black/charcoal */
[data-testid="stChatMessage"], [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div {
    color: #111827 !important;
}

/* CRITICAL FIX FOR FULL-WIDTH EDGE-TO-EDGE VIEWPORT
   Unsets max-width restraints and strips default framework bounding gutters
*/
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 100% !important;
}

/* Custom Side Disclaimer Panel Style */
.side-disclaimer {
    background-color: #FFF6ED;
    border: 1px solid #FFEDD5;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    display: flex;
    gap: 12px;
}
.side-disclaimer-icon {
    font-size: 18px;
    color: #C2410C;
    font-weight: bold;
}
.side-disclaimer-text {
    font-size: 13px;
    color: #9A3412;
    line-height: 1.5;
}

/* Elegant Custom Top Header Bar */
.custom-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 0;
    margin-bottom: 20px;
}
.brand-block {
    display: flex;
    align-items: center;
    gap: 12px;
}
.brand-badge {
    background-color: #0F5A41;
    color: white;
    font-weight: 700;
    font-size: 16px;
    padding: 8px 12px;
    border-radius: 12px;
}
.brand-name {
    font-size: 20px;
    font-weight: 700;
    color: #111827;
    line-height: 1.1;
}
.brand-tag {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #6B7280;
}
.custom-nav-links {
    display: flex;
    gap: 24px;
    font-size: 14.5px;
    font-weight: 500;
    color: #4B5563;
}
.custom-nav-links a {
    text-decoration: none !important;
    color: inherit !important;
}
.custom-nav-links span.active {
    color: #0F5A41;
    font-weight: 600;
    border-bottom: 2px solid #0F5A41;
    padding-bottom: 4px;
}

/* ─────────────────────────────────────────────
    UNIFIED HERO CONTAINER SYSTEM
   ───────────────────────────────────────────── */
.hero-wrapper {
    background: radial-gradient(circle at 80% 20%, #115E46 0%, #063728 100%);
    border-radius: 24px;
    padding: 48px;
    color: white;
    position: relative;
    box-shadow: 0 10px 30px rgba(10, 60, 44, 0.15);
    margin-bottom: 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    overflow: hidden;
}
/* Blueprint Grid Overlay Line Accentuation */
.hero-wrapper::before {
    content: "";
    position: absolute;
    inset: 0;
    opacity: 0.08;
    background-image: linear-gradient(to right, rgba(255,255,255,0.4) 1px, transparent 1px), 
                      linear-gradient(to bottom, rgba(255,255,255,0.4) 1px, transparent 1px);
    background-size: 32px 32px;
    z-index: 1;
}
.hero-left-content { 
    max-width: 58%; 
    z-index: 2; 
    display: flex; 
    flex-direction: column;
    align-items: flex-start;
}
.hero-badge-top {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #34D399;
    font-size: 11px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 20px;
    margin-bottom: 24px;
    letter-spacing: 0.2px;
}
.hero-main-title {
    font-size: 42px;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 20px;
    color: #FFFFFF;
}
.hero-main-title span { color: #FBBF24; }
.hero-description {
    font-size: 15px;
    line-height: 1.6;
    color: #A7F3D0;
    margin-bottom: 32px;
}

/* Button Layout Array Group */
.hero-btn-group {
    display: flex;
    gap: 16px;
}
.btn-dynamic-chat {
    background-color: #10B981;
    color: #042F22 !important;
    font-weight: 700;
    font-size: 14px;
    padding: 12px 24px;
    border-radius: 12px;
    text-decoration: none !important;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    border: none;
    transition: transform 0.2s, background-color 0.2s;
}
.btn-dynamic-chat:hover {
    background-color: #059669;
    transform: translateY(-1px);
}
.btn-browse-library {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #FFFFFF !important;
    font-weight: 600;
    font-size: 14px;
    padding: 12px 24px;
    border-radius: 12px;
    text-decoration: none !important;
    display: inline-flex;
    align-items: center;
    transition: background-color 0.2s;
}
.btn-browse-library:hover {
    background: rgba(255, 255, 255, 0.1);
}

/* Right Floating Card Dashboard */
.hero-right-dashboard {
    z-index: 2;
    width: 380px;
}
.system-health-card-unified {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 24px;
}
.health-header-unified {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.health-title-text {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #94A3B8;
}
.health-badge-secure {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 8px;
    letter-spacing: 0.5px;
}
.health-skeleton-line {
    height: 6px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 4px;
    margin-bottom: 12px;
}
.health-skeleton-line.l1 { width: 60%; }
.health-skeleton-line.l2 { width: 85%; }
.health-skeleton-line.l3 { width: 68%; }
.health-footer-unified {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 28px;
    font-size: 12px;
}

/* Modern Minimalist Service Cards Layout */
.cards-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    margin-bottom: 35px;
}
.target-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 20px 16px;
    transition: all 0.2s ease;
}
.target-card:hover {
    border-color: #10B981;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}
.target-card.active-card {
    border: 2px solid #000000;
    box-shadow: 0 0 0 1px #000000;
}
.target-card .card-icon {
    font-size: 24px;
    margin-bottom: 12px;
}
.target-card .card-title {
    font-size: 15px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 4px;
}
.target-card .card-subtext {
    font-size: 12px;
    color: #6B7280;
}

/* Right Side Dashboard Panels */
.side-panel {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}
.panel-title {
    font-size: 14px;
    font-weight: 700;
    color: #1E293B;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
}

/* Styled Links for the Verification Hub */
.hub-link-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #E2E8F0;
    font-size: 13px;
    text-decoration: none !important;
    color: #1E293B !important;
    font-weight: 500;
    transition: color 0.2s ease;
}
.hub-link-item:last-child {
    border-bottom: none;
}
.hub-link-item:hover {
    color: #0F5A41 !important; 
}
.hub-link-arrow {
    font-size: 11px;
    color: #64748B;
}

/* Custom Library/Data Tables UI */
.library-wrapper {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 24px;
    margin-top: 30px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.library-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}
.library-title {
    font-size: 20px;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.3px;
}
.select-filter-label-group {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13.5px;
    font-weight: 600;
    color: #4B5563;
}

/* Custom Table Layout Array styling */
.custom-table-container {
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    overflow: hidden;
}
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
    text-align: left;
}
.custom-table th {
    background-color: #F8FAFC;
    color: #1F2937;
    font-weight: 700;
    padding: 16px 18px;
    border-bottom: 1px solid #E2E8F0;
    border-right: 1px solid #E2E8F0;
    font-size: 12.5px;
    letter-spacing: 0.2px;
}
.custom-table th:last-child {
    border-right: none;
}
.custom-table td {
    padding: 20px 18px;
    border-bottom: 1px solid #E2E8F0;
    border-right: 1px solid #E2E8F0;
    vertical-align: top;
    line-height: 1.6 !important;
}
.custom-table td:last-child {
    border-right: none;
}
.custom-table tbody tr:last-child td {
    border-bottom: none;
}
.custom-table tbody tr:nth-child(even) {
    background-color: #F8FAFC;
}
.custom-table tbody tr:nth-child(odd) {
    background-color: #FFFFFF;
}
.table-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
</style>
""")
 
# Handle RTL / Arabic Styles Dynamic Loading
if is_arabic:
    st.html("""
    <style>
    html, body, [class*="css"], .stApp { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; }
    .custom-header, .hero-wrapper, .library-header-row { flex-direction: row-reverse; }
    .custom-table { text-align: right; }
    .custom-table th, .custom-table td { border-left: 1px solid #E2E8F0; border-right: none; }
    .custom-table th:last-child, .custom-table td:last-child { border-left: none; }
    .hub-link-item { flex-direction: row-reverse; }
    .side-disclaimer { flex-direction: row-reverse; }
    .hero-btn-group { flex-direction: row-reverse; }
    .select-filter-label-group { flex-direction: row-reverse; }
    </style>
    """)

# ─────────────────────────────────────────────
# STATE TRACKING
# ─────────────────────────────────────────────
if "selected_library_filter" not in st.session_state:
    st.session_state.selected_library_filter = "All"

if "messages" not in st.session_state:
    st.session_state.messages = []

# ─────────────────────────────────────────────
# CONFIGURATION/SIDEBAR ACCESS
# ─────────────────────────────────────────────
with st.sidebar:
    st.header(t["config_header"])
    api_key_input = get_rotated_api_key()
    if len(API_KEYS_POOL) > 0:
        st.success(t["api_loaded"])
    else:
        api_key_input = st.text_input(t["api_label"], type="password", help=t["api_help"])
        if not api_key_input: st.info(t["api_info"])
 
    if st.button(t["clear_chat"]):
        st.session_state.messages = []
        st.session_state.pop("chat_session", None)
        st.session_state.pop("active_api_key", None)
        st.rerun()
 
# ─────────────────────────────────────────────
# UNIFIED NAV BAR WITH TOP PADDING SHIFT
# ─────────────────────────────────────────────
lang_toggle_text = "English" if is_arabic else "العربية"
current_filter = st.session_state.selected_library_filter

active_all = "active" if current_filter == "All" else ""
active_visa = "active" if current_filter == "Visa Services" else ""
active_driving = "active" if current_filter == "Driving License" else ""
active_business = "active" if current_filter == "Business License" else ""

navbar_html = f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 5px 0; margin-bottom: 20px; width: 100%;">
    
    <div class="brand-block" style="flex: 1; display: flex; justify-content: flex-start;">
        <div class="brand-badge">AE</div>
        <div>
            <div class="brand-name">{t["nav_logo"]}</div>
            <div class="brand-tag">Prototype Agent</div>
        </div>
    </div>
    
    <div style="flex: 2; display: flex; justify-content: center; align-items: center;">
        <div class="custom-nav-links" style="gap: 32px; font-size: 14.5px; display: flex; align-items: center;">
            <a href="?filter=All#verified-library" target="_self">
                <span class="{active_all}">{t["nav_home"]}</span>
            </a>
            <a href="?filter=Visa+Services#verified-library" target="_self">
                <span class="{active_visa}">{t["nav_visa"]}</span>
            </a>
            <a href="?filter=Driving+License#verified-library" target="_self">
                <span class="{active_driving}">{t["nav_driving"]}</span>
            </a>
            <a href="?filter=Business+License#verified-library" target="_self">
                <span class="{active_business}">{t["nav_business"]}</span>
            </a>
        </div>
    </div>
    
    <div style="flex: 1; display: flex; justify-content: flex-end; align-items: center;">
        <a href="?click=lang_toggle" target="_self" style="
            text-decoration: none; 
            color: #0F5A41; 
            font-weight: 600; 
            font-size: 15px; 
            padding: 6px 14px; 
            border: 1px solid #E5E7EB; 
            border-radius: 10px; 
            background-color: #FFFFFF;
            box-shadow: 0px 1px 2px rgba(0,0,0,0.05);
            transition: background 0.2s;
        " onmouseover="this.style.backgroundColor='#F9FAFB'" onmouseout="this.style.backgroundColor='#FFFFFF'">
            {lang_toggle_text}
        </a>
    </div>
    
</div>
<div style="margin-bottom: 25px;"></div>
"""
st.html(navbar_html)

# ─────────────────────────────────────────────
# PARSE ACTION & LANGUAGE HOOKS FROM URL PARAMS
# ─────────────────────────────────────────────
url_params = st.query_params

if "filter" in url_params:
    requested_filter = url_params.get("filter")
    if requested_filter in ["All", "Visa Services", "Driving License", "Business License"]:
        st.session_state.selected_library_filter = requested_filter
    st.query_params.clear()
    st.rerun()

if url_params.get("click") == "lang_toggle":
    st.query_params.clear()
    st.session_state.lang = "Arabic" if st.session_state.lang == "English" else "English"
    st.session_state.pop("chat_session", None)
    st.session_state.messages = []
    st.rerun()

if url_params.get("action") == "start_chat":
    st.query_params.clear()
    if len(st.session_state.messages) <= 1:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Dynamic chat initialized! How can I guide you through UAE government services today?",
            "sources": []
        })
    st.rerun()

# ─────────────────────────────────────────────
# HERO BANNER LAYOUT VIA NATIVE STREAMLIT HTML
# ─────────────────────────────────────────────
hero_raw_html = f"""
<div class="hero-wrapper">
    <div class="hero-left-content">
        <div class="hero-main-title">UAE Government<br><span>Services Assistant</span></div>
        <div class="hero-description">
            Get instant, reliable guidance on visas, residency rules, driving conversions, step checklists, and company registrations. Handled via fully private server-side retrieval and secure grounded AI.
        </div>
        <div class="hero-btn-group">
            <a href="?action=start_chat" target="_self" class="btn-dynamic-chat">
                Start Dynamic Chat &nbsp;➔
            </a>
            <a href="#verified-library" class="btn-browse-library">
                Browse Verification Library
            </a>
        </div>
    </div>
    <div class="hero-right-dashboard">
        <div class="system-health-card-unified">
            <div class="health-header-unified">
                <div class="health-title-text">SYSTEM HEALTH</div>
                <div class="health-badge-secure">SECURE</div>
            </div>
            <div class="health-skeleton-line l1"></div>
            <div class="health-skeleton-line l2"></div>
            <div class="health-skeleton-line l3"></div>
            <div class="health-footer-unified">
                <span style="color:#64748B;">Server-side retrieval:</span>
                <span style="color:#FBBF24; font-family:monospace; font-weight:700;">TF-IDF Vectorizer</span>
            </div>
        </div>
    </div>
</div>
"""
st.html(hero_raw_html)
 
# ─────────────────────────────────────────────
# DYNAMIC CONFIGURABLE CARDS LAYOUT
# ─────────────────────────────────────────────
st.html(f"""
<div class="cards-row">
    <div class="target-card {'active-card' if current_filter == 'Visa Services' else ''}">
        <div class="card-icon">🛂</div>
        <div class="card-title">{t["svc_visa"]}</div>
        <div class="card-subtext">Golden, Student, Resident</div>
    </div>
    <div class="target-card {'active-card' if current_filter == 'Driving License' else ''}">
        <div class="card-icon">🚗</div>
        <div class="card-title">{t["svc_driving"]}</div>
        <div class="card-subtext">Convert, Renew, Eye Tests</div>
    </div>
    <div class="target-card {'active-card' if current_filter == 'Business License' else ''}">
        <div class="card-icon">🏢</div>
        <div class="card-title">{t["svc_business"]}</div>
        <div class="card-subtext">Freezone, Virtual Licenses</div>
    </div>
    <div class="target-card">
        <div class="card-icon">🔄</div>
        <div class="card-title">{t["svc_renewals"]}</div>
        <div class="card-subtext">Emirates ID, Fine Clearance</div>
    </div>
    <div class="target-card {'active-card' if current_filter == 'All' else ''}">
        <div class="card-icon">❓</div>
        <div class="card-title">Full Directory</div>
        <div class="card-subtext">Check the full library</div>
    </div>
</div>
""")
 
# ─────────────────────────────────────────────
# SPLIT INTERACTIVE CONTEXT LAYOUT (Chat + Details Panels)
# ─────────────────────────────────────────────
if api_key_input and "chat_session" not in st.session_state:
    model = get_gemini_model(api_key_input)
    st.session_state.chat_session = start_chat_session(model)
 
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": t["greeting"],
        "sources": [],
    })

chat_col, sidebar_col = st.columns([2, 1])

with chat_col:
    st.markdown(f"#### 🤖 {t['chat_section']}")
    
    st.markdown(f"<span style='font-size:13px; font-weight:600; color:#6B7280;'>{t['quick_queries']}</span>", unsafe_allow_html=True)
    q_btn_cols = st.columns(3)
    quick_query = None
    with q_btn_cols[0]:
        if st.button(t["btn_student"]): quick_query = t["q_student"]
    with q_btn_cols[1]:
        if st.button(t["btn_driving"]): quick_query = t["q_driving"]
    with q_btn_cols[2]:
        if st.button(t["btn_golden"]): quick_query = t["q_golden"]
        
    if quick_query and api_key_input:
        matched_docs, context_string = retrieve_context(quick_query, vectorizer, tfidf_matrix, kb_data)
        reply = generate_grounded_response(quick_query, context_string, st.session_state.chat_session, lang=st.session_state.lang)
        st.session_state.messages.append({"role": "user", "content": quick_query, "sources": []})
        st.session_state.messages.append({"role": "assistant", "content": reply, "sources": matched_docs})
        st.rerun()

    st.markdown('<div style="background:white; border:1px solid #E5E7EB; border-radius:16px; padding:20px; margin-top:10px;">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    if user_input := st.chat_input(t["placeholder"]):
        if not api_key_input:
            st.warning(t["api_info"])
        else:
            st.session_state.messages.append({"role": "user", "content": user_input, "sources": []})
            matched_docs, context_string = retrieve_context(user_input, vectorizer, tfidf_matrix, kb_data)
            with st.spinner(t["thinking"]):
                reply = generate_grounded_response(user_input, context_string, st.session_state.chat_session, lang=st.session_state.lang)
            st.session_state.messages.append({"role": "assistant", "content": reply, "sources": matched_docs})
            st.rerun()

with sidebar_col:
    st.html(f"""
    <div class="side-disclaimer">
        <div class="side-disclaimer-icon">🛈</div>
        <div class="side-disclaimer-text">
            <strong>Prototype Disclaimer:</strong> This website is an independent AI prototype built for research and demonstration. It is NOT an official UAE government portal. Always consult and verify regulations directly on official gov source links.
        </div>
    </div>
    """)

    st.html(f"""
    <div class="side-panel">
        <div class="panel-title">🗂️ Trusted Verification Hubs</div>
        <a href="https://u.ae" target="_blank" class="hub-link-item">
            <span>Official UAE Portal</span><span class="hub-link-arrow">↗</span>
        </a>
        <a href="https://icp.gov.ae" target="_blank" class="hub-link-item">
            <span>ICP National Portal</span><span class="hub-link-arrow">↗</span>
        </a>
        <a href="https://gdrfad.gov.ae" target="_blank" class="hub-link-item">
            <span>GDRFA Dubai Services</span><span class="hub-link-arrow">↗</span>
        </a>
        <a href="https://rta.ae" target="_blank" class="hub-link-item">
            <span>RTA Traffic Portal</span><span class="hub-link-arrow">↗</span>
        </a>
        <a href="https://mohre.gov.ae" target="_blank" class="hub-link-item">
            <span>MOHRE Labour Agency</span><span class="hub-link-arrow">↗</span>
        </a>
    </div>
    """)

# ─────────────────────────────────────────────
# PIXEL-PERFECT VERIFIED SERVICES LIBRARY MATRIX 
# ─────────────────────────────────────────────
st.html('<div id="verified-library"></div>')
st.html('<div class="library-wrapper">')

lib_header_left, lib_header_right = st.columns([3, 2])

with lib_header_left:
    st.html(f'<div class="library-title">📚 Verified Services Library ({st.session_state.selected_library_filter})</div>')
    st.html(
        '<p style="font-size:13px; color:#6B7280; margin-top: 4px; margin-bottom:0;">'
        'Verify criteria, checklists, fee lists, and wait times loaded securely from the agent source.'
        '</p>'
    )

with lib_header_right:
    st.html('<div class="select-filter-label-group">🔍 Filter Dataset Directory:</div>')
    filter_options = ["All", "Visa Services", "Driving License", "Business License"]
    try:
        current_index = filter_options.index(st.session_state.selected_library_filter)
    except ValueError:
        current_index = 0
        
    selected_option = st.selectbox(
        label="Filter Dataset Directory",
        options=filter_options,
        index=current_index,
        label_visibility="collapsed",
        key="directory_filter_dropdown"
    )
    if selected_option != st.session_state.selected_library_filter:
        st.session_state.selected_library_filter = selected_option
        st.rerun()

st.html("<br>")

all_library_items = [
    {
        "category": "Visa Services",
        "title": "Student Visa Residency Guide",
        "badge": "Residency",
        "badge_bg": "#EFF6FF", "badge_color": "#1D4ED8",
        "eligibility": "Students who are at least 18 years old and studying in an accredited UAE university, college, or academic institution, sponsored by their parent or the educational institution itself.",
        "checklist": "<strong>Primary documents:</strong><br>• Official admission letter<br>• Valid passport copy<br>• Medical fitness certificate<br>• Health insurance card details",
        "timeline": "🕒 10 to 15 working days.",
        "fees": "Registration fee is AED 150. Residency visa issuance fee is AED 100 per year of study. Medical test fee is AED 250."
    },
    {
        "category": "Driving License",
        "title": "Convert Foreign Driving License to UAE License",
        "badge": "Conversions",
        "badge_bg": "#ECFDF5", "badge_color": "#047857",
        "eligibility": "Holders of a valid national driving license from approved countries (including GCC, UK, US, Canada, EU nations, Japan, Singapore, Australia) who possess a valid UAE residence visa.",
        "checklist": "<strong>Primary documents:</strong><br>• Valid foreign driving license<br>• Certified legal translation<br>• Valid Emirates ID card<br>• Optical test clearance slip",
        "timeline": "🕒 Same-day service (immediate printing).",
        "fees": "File opening fee: AED 200, License issuance fee: AED 600, Knowledge and innovation fee: AED 20."
    },
    {
        "category": "Visa Services",
        "title": "UAE Golden Visa Options and Eligibility",
        "badge": "Golden Visa",
        "badge_bg": "#F5F3FF", "badge_color": "#6D28D9",
        "eligibility": "Real estate investors (property worth AED 2 million or more), entrepreneurs (with capital of AED 500k+), highly talented professionals, scientists, researchers, doctors, and exceptional outstanding students.",
        "checklist": "<strong>Primary documents:</strong><br>• Property title deed proof<br>• Accredited degree certificate<br>• Professional recommendation letters<br>• Complete active audit reports",
        "timeline": "🕒 7 to 10 working days.",
        "fees": "Nomination request fee: AED 150, 10-year Golden Visa fee: AED 2,800, Emirates ID charge: AED 1,000."
    },
    {
        "category": "Driving License",
        "title": "UAE Driving License Renewal Process",
        "badge": "Renewals",
        "badge_bg": "#FFFBEB", "badge_color": "#B45309",
        "eligibility": "All residents and citizens holding an active or expired UAE driving license. Active licenses can be renewed up to 1 year prior to expiry.",
        "checklist": "<strong>Primary documents:</strong><br>• Valid Emirates ID card<br>• Expired driving license log<br>• Registered eye test record",
        "timeline": "🕒 3 to 5 working days for delivery; digital version available immediately.",
        "fees": "Renewal fee for age 21+: AED 300, Fee for under 21: AED 100, Eye test: AED 150-180, Courier charge: AED 25."
    },
    {
        "category": "Business License",
        "title": "Dubai Virtual Company License Guide",
        "badge": "Formation",
        "badge_bg": "#FEF2F2", "badge_color": "#B91C1C",
        "eligibility": "Global business owners and non-residents from over 100 approved countries, for sectors including creative, technology, and services.",
        "checklist": "<strong>Primary documents:</strong><br>• Valid passport identification<br>• Global residency verification<br>• Corporate background screening",
        "timeline": "🕒 25 to 30 working days.",
        "fees": "1-year virtual license: USD 233 (AED 850), Registry fee: USD 100."
    }
]

filtered_items = [
    item for item in all_library_items 
    if st.session_state.selected_library_filter == "All" or item["category"] == st.session_state.selected_library_filter
]

table_rows = []
for item in filtered_items:
    row_html = (
        f"<tr>"
        f"<td style='width: 22%;'><strong style='color: #111827; font-size: 14.5px; display: block; margin-bottom: 8px;'>{item['title']}</strong>"
        f"<span class='table-badge' style='background:{item['badge_bg']}; color:{item['badge_color']};'>{item['badge']}</span></td>"
        f"<td style='width: 23%; color:#374151;'>{item['eligibility']}</td>"
        f"<td style='width: 23%; color:#374151;'>{item['checklist']}</td>"
        f"<td style='width: 14%; color:#4B5563; font-weight: 500;'>{item['timeline']}</td>"
        f"<td style='width: 18%; color:#111827; font-weight: 600; text-align:right;'>{item['fees']}</td>"
        f"</tr>"
    )
    table_rows.append(row_html)

if not table_rows:
    table_rows_html = "<tr><td colspan='5' style='text-align:center; padding:40px; color:#9CA3AF;'>No records available for this filter group.</td></tr>"
else:
    table_rows_html = "".join(table_rows)

full_matrix_html = (
    "<div class='custom-table-container'>"
    "<table class='custom-table'>"
    "<thead>"
    "<tr>"
    "<th style='width: 22%;'>Service Title / Tag</th>"
    "<th style='width: 23%;'>Typical Eligibility Criteria</th>"
    "<th style='width: 23%;'>Required Checklists</th>"
    "<th style='width: 14%;'>Processing Timeline</th>"
    "<th style='width: 18%; text-align:right;'>Standard Fees</th>"
    "</tr>"
    "</thead>"
    "<tbody>"
    f"{table_rows_html}"
    "</tbody>"
    "</table>"
    "</div>"
    "</div>"
)

st.html(full_matrix_html)

# ─────────────────────────────────────────────
# PROTOTYPE DARK BOTTOM FOOTER BAR
# ─────────────────────────────────────────────
st.html("""
<style>
.custom-footer-bar {
    background-color: #0B132B;
    color: #94A3B8;
    padding: 30px 60px;
    margin: 60px -100px -50px -100px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
}
.footer-left-side {
    display: flex;
    align-items: center;
    gap: 16px;
}
.footer-logo-badge {
    color: #FFFFFF;
    font-weight: 700;
    font-size: 15px;
    opacity: 0.8;
}
.footer-title-text strong {
    color: #FFFFFF;
    display: block;
    font-size: 14px;
    margin-bottom: 2px;
}
.footer-title-text span {
    color: #475569;
    font-size: 12px;
}
.footer-right-side {
    display: flex;
    align-items: center;
    gap: 20px;
}
.session-tag-highlight {
    color: #10B981;
    font-family: monospace;
    font-weight: 700;
}
.footer-link-anchor {
    color: #475569;
    text-decoration: underline;
    cursor: pointer;
}
</style>

<div class="custom-footer-bar">
    <div class="footer-left-side">
        <div class="footer-logo-badge">AE</div>
        <div class="footer-title-text">
            <strong>UAE Gov services AI Assistant Prototype</strong>
            <span>Decoupled UI and Agent Full Stack React/Express Architecture</span>
        </div>
    </div>
    <div class="footer-right-side">
        <div>Active Session: <span class="session-tag-highlight">session_v3exrrfa3</span></div>
        <div style="color: #475569;">•</div>
        <a class="footer-link-anchor" href="https://u.ae" target="_blank">Official Directory Portal</a>
    </div>
</div>
""")
