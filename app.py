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

from welcome import show_welcome_screen

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="UAE Gov Services AI Assistant",
    page_icon="🇦🇪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#--------------
st.markdown("""
<style>
/* Fix toggle button width so it never shifts layout */
div[data-testid="column"]:last-child .stButton button {
    width: 90px !important;
    text-align: center !important;
    white-space: nowrap !important;
}
</style>
""", unsafe_allow_html=True)
#---------------

# ─────────────────────────────────────────────
# STATE TRACKING INITIALIZATION (Must be done first)
# ─────────────────────────────────────────────
if "started" not in st.session_state:
    st.session_state.started = False

if "lang" not in st.session_state:
    st.session_state.lang = "English"

if "selected_library_filter" not in st.session_state:
    st.session_state.selected_library_filter = "All"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize keys array scope before validation routing blocks
API_KEYS_POOL = []

# ─────────────────────────────────────────────
# CONDITIONAL VIEW ROUTING
# ─────────────────────────────────────────────
if not st.session_state.started:
    # 1. SHOWS YOUR WELCOME SCREEN CARD
    show_welcome_screen()

else:
    # Safely building key arrays within clean block structures
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

    /* CRITICAL FIX FOR FULL-WIDTH EDGE-TO-EDGE VIEWPORT */
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

    /* UNIFIED HERO CONTAINER SYSTEM - SLIDESHOW VERSION */
    .hero-wrapper {
        border-radius: 24px;
        height: 420px;
        position: relative;
        box-shadow: 0 10px 30px rgba(10, 60, 44, 0.15);
        margin-bottom: 40px;
        overflow: hidden;
    }
    
    /* Sliding Engine (3 Images example) */
    .hero-slideshow {
        position: absolute;
        width: 300%; /* 100% * number of slides */
        height: 100%;
        display: flex;
        animation: heroSlider 15s infinite ease-in-out;
    }
    
    .hero-slide {
        width: 33.333%; /* 100% / number of slides */
        height: 100%;
        background-size: cover;
        background-position: center;
    }
    
    /* Animation Keyframes for Automatic Smooth Sliding */
    @keyframes heroSlider {
        0%, 28% { transform: translateX(0%); }
        33%, 61% { transform: translateX(-33.333%); }
        66%, 95% { transform: translateX(-66.666%); }
        100% { transform: translateX(0%); }
    }

    /* Cinematic Dark Tint Gradient to Guarantee Overlay Text Contrast */
    .hero-overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(to right, rgba(4, 47, 34, 0.95) 40%, rgba(4, 47, 34, 0.5) 70%, rgba(4, 47, 34, 0.2) 100%);
        z-index: 2;
    }
    
    /* Text Overlay Layout Base Container */
    .hero-content-container {
        position: absolute;
        inset: 0;
        z-index: 3;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 48px;
    }
    
    .hero-left-content { 
        max-width: 55%; 
        display: flex; 
        flex-direction: column;
        align-items: flex-start;
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
        color: #E2FBF0;
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
    }
    .btn-browse-library {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #FFFFFF !important;
        font-weight: 600;
        font-size: 14px;
        padding: 12px 24px;
        border-radius: 12px;
        text-decoration: none !important;
        backdrop-filter: blur(4px);
    }

    .hero-right-dashboard {
        width: 380px;
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
    }
    .target-card.active-card {
        border: 2px solid #000000;
    }
    .target-card .card-icon { font-size: 24px; margin-bottom: 12px; }
    .target-card .card-title { font-size: 15px; font-weight: 700; color: #111827; }
    .target-card .card-subtext { font-size: 12px; color: #6B7280; }

    /* Right Side Dashboard Panels */
    .side-panel {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
    }
    .panel-title {
        font-size: 14px;
        font-weight: 700;
        color: #1E293B;
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
        color: #1E293B !important;
        text-decoration: none !important;
    }

    /* Custom Library/Data Tables UI */
    .library-wrapper {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 24px;
        margin-top: 30px;
    }
    .library-title { font-size: 20px; font-weight: 700; color: #111827; }

    /* Table Layout Structure */
    .custom-table-container { border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden; }
    .custom-table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
    .custom-table th { background-color: #F8FAFC; color: #1F2937; font-weight: 700; padding: 16px 18px; text-align: left; }
    .custom-table td { padding: 20px 18px; border-bottom: 1px solid #E2E8F0; vertical-align: top; }
    .table-badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; }
    
    /* Footer Style Class */
    .custom-footer-bar { padding: 20px; text-align: center; color: #6B7280; font-size: 12px; margin-top: 40px; }
    </style>
    """)

if is_arabic:
    st.html("""
    <style>
    html, body, [class*="css"], .stApp { 
        font-family: 'Cairo', sans-serif !important; 
        direction: rtl; 
        text-align: right; 
    }
    
    /* ── SLIDESHOW EXCEPTION — must stay LTR ── */
    .hero-slideshow { direction: ltr !important; }
    .hero-slide     { direction: ltr !important; }

    /* Keep text inside hero RTL */
    .hero-left-content,
    .hero-main-title,
    .hero-description,
    .hero-btn-group { 
        direction: rtl !important; 
        text-align: right !important; 
    }
    
    .custom-header, .hero-wrapper, .library-header-row { flex-direction: row-reverse; }
    .custom-table { text-align: right; }
    .custom-table th { text-align: right; }
    .hub-link-item { flex-direction: row-reverse; }
    .side-disclaimer { flex-direction: row-reverse; }
    .hero-btn-group { flex-direction: row-reverse; }

    /* Force slideshow to always animate LTR regardless of page direction */
    .hero-slideshow,
    .hero-slide {
        direction: ltr !important;
        unicode-bidi: isolate !important;
    }
    
    /* Override the animation with an identical one using positive translateX for RTL */
    @keyframes heroSliderRTL {
        0%        { transform: translateX(0%); }
        28%       { transform: translateX(0%); }
        33%       { transform: translateX(-33.333%); }
        61%       { transform: translateX(-33.333%); }
        66%       { transform: translateX(-66.666%); }
        94%       { transform: translateX(-66.666%); }
        100%      { transform: translateX(0%); }
    }
    .hero-slideshow {
        animation-name: heroSliderRTL !important;
    }

    </style>
    """)


    # ─────────────────────────────────────────────
    # CONFIGURATION/SIDEBAR ACCESS (UI elements removed)
    # ─────────────────────────────────────────────
    # Fetch key to ensure backend pipeline runs continuously
    api_key_input = get_rotated_api_key()
    if len(API_KEYS_POOL) == 0 and not api_key_input:
        # Fallback in case no server-side keys exist to allow manual testing
        with st.sidebar:
            api_key_input = st.text_input(t["api_label"], type="password", help=t["api_help"])

    # Clear chat utility option remains hosted cleanly within the collapsible tray
    with st.sidebar:
        if st.button(t["clear_chat"]):
            st.session_state.messages = []
            st.session_state.pop("chat_session", None)
            st.session_state.pop("active_api_key", None)
            st.rerun()
     
    # ─────────────────────────────────────────────
    # UNIFIED NAV BAR
    # ─────────────────────────────────────────────
    lang_toggle_text = "English" if is_arabic else "العربية"
    current_filter = st.session_state.selected_library_filter

    active_all = "active" if current_filter == "All" else ""
    active_visa = "active" if current_filter == "Visa Services" else ""
    active_driving = "active" if current_filter == "Driving License" else ""
    active_business = "active" if current_filter == "Business License" else ""

    # Split nav and toggle into columns
nav_col, toggle_col = st.columns([17,1])

with toggle_col:
    st.markdown("<div style='padding-top: 65px;'>", unsafe_allow_html=True)
    if st.button("English" if is_arabic else "العربية", key="lang_toggle"):
        st.session_state.lang = "Arabic" if st.session_state.lang == "English" else "English"
        st.session_state.pop("chat_session", None)
        st.session_state.messages = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with nav_col:
    st.html(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; padding:65px 0 15px 0; margin-bottom:20px;">
        <div class="brand-block" style="display:flex; align-items:center; gap:12px;">
            <div class="brand-badge">AE</div>
            <div>
                <div class="brand-name">{t["nav_logo"]}</div>
                <div class="brand-tag">Prototype Agent</div>
            </div>
        </div>
        <div class="custom-nav-links" style="gap:32px; font-size:14.5px; display:flex; align-items:center;">
            <span>{t["nav_home"]}</span>
            <span>{t["nav_visa"]}</span>
            <span>{t["nav_driving"]}</span>
            <span>{t["nav_business"]}</span>
        </div>
    </div>
    """)

    # ─────────────────────────────────────────────
    # PARSE ACTION & LANGUAGE HOOKS
    # ─────────────────────────────────────────────
    url_params = st.query_params

    if "filter" in url_params:
        requested_filter = url_params.get("filter")
        if requested_filter in ["All", "Visa Services", "Driving License", "Business License"]:
            st.session_state.selected_library_filter = requested_filter
        st.query_params.clear()
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
    # HERO BANNER LAYOUT
    # ─────────────────────────────────────────────
    hero_raw_html = f"""
    <div class="hero-wrapper">
        <div class="hero-slideshow">
            <div class="hero-slide" style="background-image: url('https://images.unsplash.com/photo-1579930700019-f5f6ba3db867?q=80&w=1176');"></div>
            <div class="hero-slide" style="background-image: url('https://images.unsplash.com/photo-1512453979798-5ea266f8880c?q=80&w=1200');"></div>
            <div class="hero-slide" style="background-image: url('https://images.unsplash.com/photo-1687754715959-41fed2161528?q=80&w=1221');"></div>
        </div>
        
        <div class="hero-overlay"></div>
        
        <div class="hero-content-container">
            <div class="hero-left-content">
                <div class="hero-main-title">UAE Government<br><span>Services Assistant</span></div>
                <div class="hero-description">
                    Get instant, reliable guidance on visas, residency rules, driving conversions, step checklists, and company registrations. Handled via fully private server-side retrieval and secure grounded AI.
                </div>
                <div class="hero-btn-group">
                    <a href="?action=start_chat" target="_self" class="btn-dynamic-chat">Start Dynamic Chat &nbsp;➔</a>
                    <a href="#verified-library" class="btn-browse-library">Browse Verification Library</a>
                </div>
            </div>
        </div>
    </div>
    """
    st.html(hero_raw_html)
     
     
    # ─────────────────────────────────────────────
    # SPLIT CHAT INTERFACE WINDOW
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
        <div class="side-panel">
            <div class="panel-title">🗂️ Trusted Verification Hubs</div>
            <a href="https://u.ae" target="_blank" class="hub-link-item"><span>Official UAE Portal</span><span class="hub-link-arrow">↗</span></a>
            <a href="https://icp.gov.ae" target="_blank" class="hub-link-item"><span>ICP National Portal</span><span class="hub-link-arrow">↗</span></a>
            <a href="https://gdrfad.gov.ae" target="_blank" class="hub-link-item"><span>GDRFA Dubai Services</span><span class="hub-link-arrow">↗</span></a>
            <a href="https://rta.ae" target="_blank" class="hub-link-item"><span>RTA Traffic Portal</span><span class="hub-link-arrow">↗</span></a>
            <a href="https://mohre.gov.ae" target="_blank" class="hub-link-item"><span>MOHRE Labour Agency</span><span class="hub-link-arrow">↗</span></a>
        </div>
        """)

    # ─────────────────────────────────────────────
    # VERIFIED SERVICES LIBRARY MATRIX 
    # ─────────────────────────────────────────────
    st.html('<div id="verified-library"></div>')
    st.html('<div class="library-wrapper">')

    lib_header_left, lib_header_right = st.columns([3, 2])

    with lib_header_left:
        st.html(f'<div class="library-title">📚 Verified Services Library ({st.session_state.selected_library_filter})</div>')
        st.html('<p style="font-size:13px; color:#6B7280; margin-top: 4px; margin-bottom:0;">Verify criteria, checklists, fee lists, and wait times loaded securely from the agent source.</p>')

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
    # PROTOTYPE BOTTOM FOOTER BAR
    # ─────────────────────────────────────────────
    st.html("""
    <div class="custom-footer-bar">
        © 2026 Engineering Prototype Framework Platform Assembly. Developed for Research Sandbox Evaluations.
    </div>
    """)
