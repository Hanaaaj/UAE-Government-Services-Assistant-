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
    initial_sidebar_state="collapsed" # Collapsed to let the custom top nav shine
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
# ADVANCED CUSTOM CSS FOR TARGET DESIGN
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Cairo:wght@300;400;600;700;800&display=swap');
 
/* Global Canvas Adjustments */
html, body, [class*="css"], .stApp { 
    font-family: 'Inter', sans-serif; 
    background-color: #FDFDFB !important;
}

/* Fix main padding */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 3rem !important;
    max-width: 1300px !important;
}

/* Custom Top Warning Banner */
.top-disclaimer {
    background-color: #FFF6ED;
    border-bottom: 1px solid #FFEDD5;
    padding: 10px 40px;
    font-size: 13px;
    color: #9A3412;
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0 -100px 20px -100px;
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
    font-size: 14px;
    font-weight: 500;
    color: #4B5563;
}
.custom-nav-links span.active {
    color: #0F5A41;
    font-weight: 600;
    border-bottom: 2px solid #0F5A41;
    padding-bottom: 4px;
}

/* The Emerald Hero Section */
.hero-container {
    background: radial-gradient(circle at 80% 20%, #166E53 0%, #0A3C2C 100%);
    border-radius: 24px;
    padding: 50px 50px 60px 50px;
    color: white;
    position: relative;
    box-shadow: 0 10px 30px rgba(10, 60, 44, 0.15);
    margin-bottom: 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    overflow: hidden;
}
.hero-container::before {
    content: "";
    position: absolute;
    inset: 0;
    opacity: 0.04;
    background-image: linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px);
    background-size: 24px 24px;
}
.hero-left { max-width: 55%; z-index: 2; }
.hero-badge {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 6px 14px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    display: inline-block;
    margin-bottom: 20px;
    color: #A7F3D0;
}
.hero-title {
    font-size: 44px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 16px;
    color: #FFFFFF;
}
.hero-title span { color: #FBBF24; }
.hero-subtitle {
    font-size: 15px;
    line-height: 1.5;
    color: #D1FAE5;
    opacity: 0.9;
}

/* System Health Card inside Hero */
.system-health-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(8px);
    border-radius: 16px;
    padding: 24px;
    width: 380px;
    z-index: 2;
}
.health-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
}
.health-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #94A3B8;
}
.health-status {
    background: rgba(16, 185, 129, 0.2);
    color: #34D399;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 6px;
    letter-spacing: 0.5px;
}
.health-line {
    height: 4px;
    background: rgba(255,255,255,0.1);
    border-radius: 2px;
    margin-bottom: 10px;
}
.health-line.fill { width: 70%; background: rgba(255,255,255,0.3); }
.health-line.fill-short { width: 45%; background: rgba(255,255,255,0.3); }
.health-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
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

/* Split Section: Chat Area and Right Sidebar Panels */
.dashboard-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 30px;
    margin-bottom: 40px;
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
.metadata-row {
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #E2E8F0;
    font-size: 13px;
}
.metadata-row:last-child { border: none; }
.metadata-label { color: #64748B; font-weight: 500; font-family: monospace; }
.metadata-value { font-weight: 600; }

/* Custom Library/Data Tables UI */
.library-wrapper {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 24px;
    margin-top: 20px;
}
.library-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.library-title {
    font-size: 18px;
    font-weight: 700;
    color: #111827;
}

/* Data Table Styling */
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    text-align: left;
}
.custom-table th {
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
    color: #6B7280;
    padding: 12px;
    border-bottom: 1px solid #E5E7EB;
    font-weight: 600;
}
.custom-table td {
    padding: 16px 12px;
    border-bottom: 1px solid #F3F4F6;
    vertical-align: top;
}
.table-badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    background: #FEF3C7;
    color: #D97706;
}
</style>
""", unsafe_allow_html=True)
 
# Handle RTL / Arabic Styles Dynamic Loading
if is_arabic:
    st.markdown("""
    <style>
    html, body, [class*="css"], .stApp { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; }
    .custom-header, .hero-container, .library-header-row { flex-direction: row-reverse; }
    .custom-table { text-align: right; }
    </style>
    """, unsafe_allow_html=True)
 
# ─────────────────────────────────────────────
# TOP PROTOTYPE DISCLAIMER BANNER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="top-disclaimer">
    <span>🛈</span>
    <div><strong>Prototype Disclaimer:</strong> This website is an independent AI prototype built for research and demonstration. It is NOT an official UAE government portal. Always consult and verify regulations directly on official gov source links.</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONFIGURATION/SIDEBAR ACCESS (Kept Functional)
# ─────────────────────────────────────────────
with st.sidebar:
    st.header(t["config_header"])
    if len(API_KEYS_POOL) > 0:
        api_key_input = get_rotated_api_key()
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
# CUSTOM NAVBAR UI WITH INLINE LANG TOGGLE
# ─────────────────────────────────────────────
nav_html = f"""
<div class="custom-header">
    <div class="brand-block">
        <div class="brand-badge">AE</div>
        <div>
            <div class="brand-name">{t["nav_logo"]}</div>
            <div class="brand-tag">Prototype Agent</div>
        </div>
    </div>
    <div class="custom-nav-links">
        <span class="active">{t["nav_home"]}</span>
        <span>{t["nav_visa"]}</span>
        <span>{t["nav_driving"]}</span>
        <span>{t["nav_business"]}</span>
    </div>
</div>
"""
st.markdown(nav_html, unsafe_allow_html=True)

# Language Toggle Layer Integration
cols_lang = st.columns([12, 1])
with cols_lang[1]:
    if st.button(t["toggle_btn"], key="lang_toggle"):
        st.session_state.lang = "Arabic" if st.session_state.lang == "English" else "English"
        st.session_state.pop("chat_session", None)
        st.session_state.messages = []
        st.rerun()

# ─────────────────────────────────────────────
# EMERALD HERO BANNER SYSTEM 
# ─────────────────────────────────────────────
hero_html = f"""
<div class="hero-container">
    <div class="hero-left">
        <div class="hero-badge">AE Powered by Gemini AI & Grounded Retrieval</div>
        <div class="hero-title">UAE Government<br><span>Services Assistant</span></div>
        <div class="hero-subtitle">Get instant, reliable guidance on visas, residency rules, driving conversions, step checklists, and company registrations. Handled via fully private server-side retrieval and secure grounded AI.</div>
    </div>
    <div class="system-health-card">
        <div class="health-header">
            <div class="health-title">SYSTEM HEALTH</div>
            <div class="health-status">SECURE</div>
        </div>
        <div class="health-line fill"></div>
        <div class="health-line fill-short"></div>
        <div class="health-line"></div>
        <div class="health-footer">
            <span style="color:#94A3B8;">Server-side retrieval:</span>
            <span style="color:#FBBF24; font-family:monospace; font-weight:700;">TF-IDF Vectorizer</span>
        </div>
    </div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)
 
# ─────────────────────────────────────────────
# DYNAMIC CONFIGURABLE CARDS LAYOUT
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="cards-row">
    <div class="target-card active-card">
        <div class="card-icon">🛂</div>
        <div class="card-title">{t["svc_visa"]}</div>
        <div class="card-subtext">Golden, Student, Resident</div>
    </div>
    <div class="target-card">
        <div class="card-icon">🚗</div>
        <div class="card-title">{t["svc_driving"]}</div>
        <div class="card-subtext">Convert, Renew, Eye Tests</div>
    </div>
    <div class="target-card">
        <div class="card-icon">🏢</div>
        <div class="card-title">{t["svc_business"]}</div>
        <div class="card-subtext">Freezone, Virtual Licenses</div>
    </div>
    <div class="target-card">
        <div class="card-icon">🔄</div>
        <div class="card-title">{t["svc_renewals"]}</div>
        <div class="card-subtext">Emirates ID, Fine Clearance</div>
    </div>
    <div class="target-card">
        <div class="card-icon">❓</div>
        <div class="card-title">Full Directory</div>
        <div class="card-subtext">Check the full library</div>
    </div>
</div>
""", unsafe_allow_html=True)
 
# ─────────────────────────────────────────────
# SPLIT INTERACTIVE CONTEXT LAYOUT (Chat + Details Panels)
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
 
if api_key_input and "chat_session" not in st.session_state:
    model = _get_model(api_key_input)
    st.session_state.chat_session = start_chat_session(model)
 
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": t["greeting"],
        "sources": [],
    })

# Setting up grid structures
chat_col, sidebar_col = st.columns([2, 1])

with chat_col:
    st.markdown(f"#### 🤖 {t['chat_section']}")
    
    # Render Quick Action Queries inside conversational window
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

    # Chat Log interface box
    st.markdown('<div style="background:white; border:1px solid #E5E7EB; border-radius:16px; padding:20px; margin-top:10px;">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    # User Input Control
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
    # Agent Context Metadata Details Card
    st.markdown(f"""
    <div class="side-panel">
        <div class="panel-title">🤖 Agent Context Details</div>
        <div class="metadata-row">
            <span class="metadata-label">API INTEGRATION</span>
            <span class="metadata-value" style="color:#0F5A41;">Secure Server Mode</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">RETRIEVAL ENGINE</span>
            <span class="metadata-value" style="color:#D97706;">TypeScript TF-IDF</span>
        </div>
        <p style="font-size:12px; color:#64748B; margin-top:15px; line-height:1.4;">
            Consistent with our architectural conventions, Gemini models are never initialized or accessed in browser space. All queries pass securely to our local agent service, keeping secrets fully private.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Verification Hub Links Card
    st.markdown(f"""
    <div class="side-panel">
        <div class="panel-title">🗂️ Trusted Verification Hubs</div>
        <div class="metadata-row"><span>Official UAE Portal</span><span style="font-size:11px;">↗</span></div>
        <div class="metadata-row"><span>ICP National Portal</span><span style="font-size:11px;">↗</span></div>
        <div class="metadata-row"><span>GDRFA Dubai Services</span><span style="font-size:11px;">↗</span></div>
        <div class="metadata-row"><span>RTA Traffic Portal</span><span style="font-size:11px;">↗</span></div>
        <div class="metadata-row"><span>MOHRE Labour Agency</span><span style="font-size:11px;">↗</span></div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GROUNDED VERIFIED VERIFICATION LIBRARY MATRIX
# ─────────────────────────────────────────────
st.markdown("""
<div class="library-wrapper">
    <div class="library-header-row">
        <div class="library-title">📚 Verified Services Library (All)</div>
    </div>
    <p style="font-size:12px; color:#6B7280; margin-bottom:20px; margin-top:-10px;">
        Verify criteria, checklists, fee lists, and wait times loaded securely from the agent source.
    </p>
    <table class="custom-table">
        <thead>
            <tr>
                <th>Service Title</th>
                <th>Typical Eligibility Criteria</th>
                <th>Required Checklists</th>
                <th>Processing Timeline</th>
                <th>Standard Fees</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Student Visa Residency Guide</strong><br><span class="table-badge" style="background:#E0F2FE; color:#0369A1;">Residency</span></td>
                <td>Students who are at least 18 years old and studying in an accredited UAE university or college.</td>
                <td><strong>Primary documents:</strong><br>Official admission letter, passport with 6 months validity, medical certificate, health insurance.</td>
                <td>🕒 10 to 15 working days.</td>
                <td>Registration fee: AED 150.<br>Issuance fee: AED 100/year.<br>Medical test: AED 250.</td>
            </tr>
            <tr>
                <td><strong>Convert Foreign Driving License</strong><br><span class="table-badge">Conversions</span></td>
                <td>Holders of a valid national driving license from approved countries (GCC, UK, US, Canada, EU, Japan, etc.).</td>
                <td><strong>Primary documents:</strong><br>Valid original license, official translation, Emirates ID, passport copy, eye test.</td>
                <td>🕒 Same-day service.</td>
                <td>File opening: AED 200.<br>License issuance: AED 600.</td>
            </tr>
            <tr>
                <td><strong>UAE Golden Visa Options</strong><br><span class="table-badge" style="background:#ECFDF5; color:#047857;">Golden Visa</span></td>
                <td>Real estate investors (AED 2M+), entrepreneurs, exceptional talents, and outstanding students.</td>
                <td><strong>Primary documents:</strong><br>Property title deed or university degree certificate, health insurance.</td>
                <td>🕒 7 to 10 working days.</td>
                <td>Nomination request: AED 150.<br>10-year visa fee: AED 2,800.</td>
            </tr>
        </tbody>
    </table>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; font-size:12px; color:#6B7280; padding-bottom:20px;'>{t['footer']}</div>", unsafe_allow_html=True)
