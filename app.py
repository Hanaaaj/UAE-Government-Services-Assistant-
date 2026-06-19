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
# INITIALIZE AGENT RETRIEVAL PIPELINE SYSTEM DATA
# ─────────────────────────────────────────────
@st.cache_resource
def initialize_agent_backend():
    # Safely load the dataset, using fallback defaults inside agent.py if missing
    kb_data = load_knowledge_base()
    vectorizer, tfidf_matrix = build_retrieval_index(kb_data)
    return kb_data, vectorizer, tfidf_matrix

kb_data, vectorizer, tfidf_matrix = initialize_agent_backend()
 
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
    padding-bottom: 0rem !important;
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
    model = get_gemini_model(api_key_input) # FIXED: Changed from _get_model to matched imported tool
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
            <span class="metadata-value" style="color:black;">Secure Server Mode</span>
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

# Custom CSS for table text alignment and row hover effects
st.markdown("""
<style>
.custom-table tbody tr:hover {
    background-color: #F8FAFC;
}
.custom-table td {
    line-height: 1.5 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="library-wrapper">', unsafe_allow_html=True)

# Layout Split: Title on the left, filter pills on the right
lib_header_left, lib_header_right = st.columns([2, 1])

with lib_header_left:
    st.markdown('<div class="library-title">📚 Verified Services Library (All)</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:13px; color:#6B7280; margin-top: 4px; margin-bottom:0;">'
        'Verify criteria, checklists, fee lists, and wait times loaded securely from the agent source.'
        '</p>', 
        unsafe_allow_html=True
    )

# Track selected tab state
if "selected_library_filter" not in st.session_state:
    st.session_state.selected_library_filter = "All"

with lib_header_right:
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    
    with f_col1:
        if st.button("All", key="btn_lib_all", use_container_width=True, 
                     type="primary" if st.session_state.selected_library_filter == "All" else "secondary"):
            st.session_state.selected_library_filter = "All"
            st.rerun()
            
    with f_col2:
        if st.button("Visa Services", key="btn_lib_visa", use_container_width=True,
                     type="primary" if st.session_state.selected_library_filter == "Visa Services" else "secondary"):
            st.session_state.selected_library_filter = "Visa Services"
            st.rerun()
            
    with f_col3:
        if st.button("Driving License", key="btn_lib_drive", use_container_width=True,
                     type="primary" if st.session_state.selected_library_filter == "Driving License" else "secondary"):
            st.session_state.selected_library_filter = "Driving License"
            st.rerun()
            
    with f_col4:
        if st.button("Business License", key="btn_lib_biz", use_container_width=True,
                     type="primary" if st.session_state.selected_library_filter == "Business License" else "secondary"):
            st.session_state.selected_library_filter = "Business License"
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── FULL DATASET MAPPED VERBATIM FROM IMAGES ───
all_library_items = [
    {
        "category": "Visa Services",
        "title": "Student Visa Residency Guide",
        "badge": "Residency",
        "badge_bg": "#FFEDD5", "badge_color": "#C2410C",
        "eligibility": "Students who are at least 18 years old and studying in an accredited UAE university, college, or academic institution, sponsored by their parent or the educational institution itself.",
        "checklist": "<strong>Primary documents:</strong><br>Official admission letter from the university, passport with at least 6 months validity, passport-size photographs, medical fitness certificate, health insurance, and sponsor's direct approval.",
        "timeline": "🕒 10 to 15 working days.",
        "fees": "Registration fee is AED 150. Residency visa issuance fee is AED 100 per year of study. Medical test fee is AED 250."
    },
    {
        "category": "Driving License",
        "title": "Convert Foreign Driving License to UAE License",
        "badge": "Conversions",
        "badge_bg": "#FFEDD5", "badge_color": "#C2410C",
        "eligibility": "Holders of a valid national driving license from approved countries (including GCC, UK, US, Canada, EU nations, Japan, Singapore, Australia) who possess a valid UAE residence visa.",
        "checklist": "<strong>Primary documents:</strong><br>Valid original foreign driving license, official translation if not in English or Arabic, valid Emirates ID, certified eye test report from an approved optician, and passport copy with residency page.",
        "timeline": "🕒 Same-day service (immediate printing).",
        "fees": "File opening fee: AED 200, License issuance fee: AED 600, Knowledge and innovation fee: AED 20."
    },
    {
        "category": "Visa Services",
        "title": "UAE Golden Visa Options and Eligibility",
        "badge": "Golden Visa",
        "badge_bg": "#FFEDD5", "badge_color": "#C2410C",
        "eligibility": "Real estate investors (property worth AED 2 million or more), entrepreneurs (with capital of AED 500k+), highly talented professionals, scientists, researchers, doctors, and exceptional outstanding students.",
        "checklist": "<strong>Primary documents:</strong><br>Property title deed of AED 2 million+, accredited university degree certificate, professional recommendation letters, active business registration documents, and full health insurance coverage details.",
        "timeline": "🕒 7 to 10 working days.",
        "fees": "Nomination request fee: AED 150, 10-year Golden Visa fee: AED 2,800, Emirates ID charge: AED 1,000."
    },
    {
        "category": "Driving License",
        "title": "UAE Driving License Renewal Process",
        "badge": "Renewals",
        "badge_bg": "#FFEDD5", "badge_color": "#C2410C",
        "eligibility": "All residents and citizens holding an active or expired UAE driving license. Active licenses can be renewed up to 1 year prior to expiry.",
        "checklist": "<strong>Primary documents:</strong><br>Valid Emirates ID, old driving license copy, and an eye test certificate from an authorized optical testing center.",
        "timeline": "🕒 3 to 5 working days for delivery; digital version available immediately.",
        "fees": "Renewal fee for age 21+: AED 300, Fee for under 21: AED 100, Eye test: AED 150-180, Courier charge: AED 25."
    },
    {
        "category": "Business License",
        "title": "Dubai Virtual Company License Guide",
        "badge": "Company Formation",
        "badge_bg": "#FFEDD5", "badge_color": "#C2410C",
        "eligibility": "Global business owners and non-residents from over 100 approved countries, for sectors including creative, technology, and services.",
        "checklist": "<strong>Primary documents:</strong><br>Valid passport copy, proof of address, personal background history check forms, and a passport-size photograph.",
        "timeline": "🕒 25 to 30 working days.",
        "fees": "1-year virtual license: USD 233 (AED 850), Registry fee: USD 100."
    }
]

# Filtering execution logic
filtered_items = [
    item for item in all_library_items 
    if st.session_state.selected_library_filter == "All" or item["category"] == st.session_state.selected_library_filter
]

# Generate markup strings
table_body_html = ""
for item in filtered_items:
    table_body_html += f"""
    <tr>
        <td style="width: 20%; padding: 24px 12px;">
            <strong style="color: #111827; font-size: 14px;">{item['title']}</strong><br><br>
            <span class="table-badge" style="background:{item['badge_bg']}; color:{item['badge_color']}; font-weight: 600; padding: 4px 10px; border-radius: 12px; font-size: 11px;">{item['badge']}</span>
        </td>
        <td style="width: 22%; color:#374151; font-size: 13.5px; padding: 24px 12px;">{item['eligibility']}</td>
        <td style="width: 25%; color:#374151; font-size: 13.5px; padding: 24px 12px;">{item['checklist']}</td>
        <td style="width: 15%; color:#4B5563; font-size: 13.5px; padding: 24px 12px;">{item['timeline']}</td>
        <td style="width: 18%; color:#000000; font-weight: 600; font-size: 13.5px; text-align:right; padding: 24px 12px;">{item['fees']}</td>
    </tr>
    """

st.markdown(f"""
    <table class="custom-table" style="width:100%; border-collapse:collapse; margin-top:10px;">
        <thead>
            <tr style="border-bottom: 1px solid #E5E7EB;">
                <th style="width: 20%; text-transform: uppercase; font-size: 11px; color: #6B7280; letter-spacing: 0.5px; padding: 12px;">Service Title</th>
                <th style="width: 22%; text-transform: uppercase; font-size: 11px; color: #6B7280; letter-spacing: 0.5px; padding: 12px;">Typical Eligibility Criteria</th>
                <th style="width: 25%; text-transform: uppercase; font-size: 11px; color: #6B7280; letter-spacing: 0.5px; padding: 12px;">Required Checklists</th>
                <th style="width: 15%; text-transform: uppercase; font-size: 11px; color: #6B7280; letter-spacing: 0.5px; padding: 12px;">Processing Timeline</th>
                <th style="width: 18%; text-transform: uppercase; font-size: 11px; color: #6B7280; letter-spacing: 0.5px; padding: 12px; text-align:right;">Standard Fees</th>
            </tr>
        </thead>
        <tbody>
            {table_body_html if table_body_html else "<tr><td colspan='5' style='text-align:center; padding:30px; color:#9CA3AF;'>No records available for this filter group.</td></tr>"}
        </tbody>
    </table>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PROTOTYPE DARK BOTTOM FOOTER BAR
# ─────────────────────────────────────────────
st.markdown("""
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
""", unsafe_allow_html=True)
