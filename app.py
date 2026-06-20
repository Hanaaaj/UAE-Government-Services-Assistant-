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
    page_title=" Public Service AI Assistant",
    page_icon="🇦🇪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# STATE TRACKING INITIALIZATION
# ─────────────────────────────────────────────
if "started" not in st.session_state:
    st.session_state.started = False

if "lang" not in st.session_state:
    st.session_state.lang = "English"

if "selected_library_filter" not in st.session_state:
    st.session_state.selected_library_filter = "All"

if "messages" not in st.session_state:
    st.session_state.messages = []

API_KEYS_POOL = []

# ─────────────────────────────────────────────
# CONDITIONAL VIEW ROUTING
# ─────────────────────────────────────────────
if not st.session_state.started:
    show_welcome_screen()

else:
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
    # AGENT BACKEND
    # ─────────────────────────────────────────────
    @st.cache_resource
    def initialize_agent_backend():
        kb_data = load_knowledge_base()
        vectorizer, tfidf_matrix = build_retrieval_index(kb_data)
        return kb_data, vectorizer, tfidf_matrix

    kb_data, vectorizer, tfidf_matrix = initialize_agent_backend()

    # ─────────────────────────────────────────────
    # BASE CSS
    # ─────────────────────────────────────────────
    st.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Cairo:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #FDFDFB !important;
    }

    [data-testid="stChatMessage"], [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div {
        color: #111827 !important;
    }

    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 100% !important;
    }

    /* Toggle button fixed width */
    div[data-testid="column"]:last-child .stButton button {
        width: 90px !important;
        text-align: center !important;
        white-space: nowrap !important;
    }

    .side-disclaimer {
        background-color: #FFF6ED;
        border: 1px solid #FFEDD5;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        display: flex;
        gap: 12px;
    }
    .side-disclaimer-icon { font-size: 18px; color: #C2410C; font-weight: bold; }
    .side-disclaimer-text { font-size: 13px; color: #9A3412; line-height: 1.5; }

    .brand-block { display: flex; align-items: center; gap: 12px; }
    .brand-badge {
        background-color: #0F5A41;
        color: white;
        font-weight: 700;
        font-size: 16px;
        padding: 8px 12px;
        border-radius: 12px;
    }
    .brand-name { font-size: 20px; font-weight: 700; color: #111827; line-height: 1.1; }
    .brand-tag { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #6B7280; }
    .custom-nav-links { display: flex; gap: 24px; font-size: 14.5px; font-weight: 500; color: #4B5563; }
    .custom-nav-links a { text-decoration: none !important; color: inherit !important; }

    /* ── HERO WRAPPER ── */
    .hero-wrapper {
        border-radius: 24px;
        height: 420px;
        position: relative;
        box-shadow: 0 10px 30px rgba(10, 60, 44, 0.15);
        margin-bottom: 40px;
        overflow: hidden;
        direction: ltr !important;
    }

    /* ── SLIDESHOW ENGINE ── */
    .hero-slideshow {
        position: absolute;
        width: 300%;
        height: 100%;
        display: flex;
        direction: ltr !important;
        unicode-bidi: isolate !important;
        animation: heroSlider 15s infinite ease-in-out;
        animation-direction: normal !important;
    }

    .hero-slide {
        width: 33.333%;
        height: 100%;
        background-size: cover;
        background-position: center;
        flex-shrink: 0;
        direction: ltr !important;
        unicode-bidi: isolate !important;
    }

    @keyframes heroSlider {
        0%,  28% { transform: translateX(0%); }
        33%, 61% { transform: translateX(-33.333%); }
        66%, 95% { transform: translateX(-66.666%); }
        100%      { transform: translateX(0%); }
    }

    /* ── HERO OVERLAY ── */
    .hero-overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(to right, rgba(4,47,34,0.95) 40%, rgba(4,47,34,0.5) 70%, rgba(4,47,34,0.2) 100%);
        z-index: 2;
    }

    /* ── HERO TEXT CONTENT ── */
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
    .hero-btn-group { display: flex; gap: 16px; }
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
        box-shadow: 0 4px 12px rgba(16,185,129,0.2);
    }
    .btn-browse-library {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.2);
        color: #FFFFFF !important;
        font-weight: 600;
        font-size: 14px;
        padding: 12px 24px;
        border-radius: 12px;
        text-decoration: none !important;
        display: inline-flex;
        align-items: center;
    }

    /* ── SERVICE CARDS ── */
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
    .target-card .card-icon { font-size: 24px; margin-bottom: 12px; }
    .target-card .card-title { font-size: 15px; font-weight: 700; color: #111827; }
    .target-card .card-subtext { font-size: 12px; color: #6B7280; }

    /* ── SIDE PANEL ── */
    .side-panel {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
    }
    .panel-title { font-size: 14px; font-weight: 700; color: #1E293B; margin-bottom: 16px; }
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

    /* ── LIBRARY TABLE ── */
    .library-wrapper {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 24px;
        margin-top: 30px;
    }
    .library-title { font-size: 20px; font-weight: 700; color: #111827; }
    .custom-table-container { border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden; }
    .custom-table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
    .custom-table th { background-color: #F8FAFC; color: #1F2937; font-weight: 700; padding: 16px 18px; text-align: left; }
    .custom-table td { padding: 20px 18px; border-bottom: 1px solid #E2E8F0; vertical-align: top; }
    .table-badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; }

    .custom-footer-bar { padding: 20px; text-align: center; color: #6B7280; font-size: 12px; margin-top: 40px; }
    </style>
    """)

    # ─────────────────────────────────────────────
    # ARABIC RTL CSS  (only added when Arabic)
    # ─────────────────────────────────────────────
    if is_arabic:
        st.html("""
        <style>
        html, body, [class*="css"], .stApp {
            font-family: 'Cairo', sans-serif !important;
            direction: rtl;
            text-align: right;
        }
        .custom-header, .library-header-row { flex-direction: row-reverse; }
        .custom-table { text-align: right; }
        .custom-table th { text-align: right; }
        .hub-link-item { flex-direction: row-reverse; }
        .side-disclaimer { flex-direction: row-reverse; }
        .hero-btn-group { flex-direction: row-reverse; }

        /* Slideshow: fully isolated from RTL */
        .hero-wrapper   { direction: ltr !important; unicode-bidi: isolate !important; }
        .hero-slideshow { direction: ltr !important; unicode-bidi: isolate !important; animation-direction: normal !important; }
        .hero-slide     { direction: ltr !important; unicode-bidi: isolate !important; }

        /* Flip overlay gradient for Arabic (dark on right side) */
        .hero-overlay {
            background: linear-gradient(
                to left,
                rgba(4,47,34,0.95) 40%,
                rgba(4,47,34,0.5)  70%,
                rgba(4,47,34,0.2)  100%
            ) !important;
        }

        /* Flip text to right side */
        .hero-content-container { direction: rtl !important; justify-content: flex-end !important; }
        .hero-left-content      { align-items: flex-end !important; text-align: right !important; }
        </style>
        """)

    # ─────────────────────────────────────────────
    # API KEY
    # ─────────────────────────────────────────────
    api_key_input = get_rotated_api_key()
    if len(API_KEYS_POOL) == 0 and not api_key_input:
        with st.sidebar:
            api_key_input = st.text_input(t["api_label"], type="password", help=t["api_help"])

    # ─────────────────────────────────────────────
    # NAV BAR + LANGUAGE TOGGLE
    # ─────────────────────────────────────────────
    nav_col, toggle_col = st.columns([17, 1])

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
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:65px 0 15px 0; margin-bottom:20px;">
            <div class="brand-block" style="display:flex; align-items:center; gap:12px;">
                <div class="brand-badge">AE</div>
                <div>
                    <div class="brand-name">{t["nav_logo"]}</div>
                    <div class="brand-tag">Prototype Agent</div>
                </div>
            </div>
            <div class="custom-nav-links" style="gap:32px; font-size:14.5px;
                                                  display:flex; align-items:center;">
                <span>{t["nav_home"]}</span>
                <span>{t["nav_visa"]}</span>
                <span>{t["nav_driving"]}</span>
                <span>{t["nav_business"]}</span>
            </div>
        </div>
        """)

    # ─────────────────────────────────────────────
    # QUERY PARAM HOOKS
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
                "content": t["greeting"],
                "sources": []
            })
        st.rerun()

    # ─────────────────────────────────────────────
    # HERO BANNER — SLIDESHOW
    # ─────────────────────────────────────────────
    hero_title    = "المدعوم بالذكاء الاصطناعي<br> مساعد الخدمات العامة" if is_arabic else "Public Service<br><span>AI Services Assistant</span>"
    hero_desc     = "احصل على إرشادات فورية وموثوقة حول التأشيرات وقواعد الإقامة وتحويل رخص القيادة والشركات." if is_arabic else "Get instant, reliable guidance on visas, residency rules, driving conversions, step checklists, and company registrations."
    hero_btn1     = "ابدأ المحادثة ←" if is_arabic else "Start Dynamic Chat &nbsp;➔"
    hero_btn2     = "تصفح المكتبة" if is_arabic else "Browse Verification Library"

    st.html(f"""
    <div class="hero-wrapper">
        <div class="hero-slideshow">
            <div class="hero-slide" style="background-image: url('https://images.unsplash.com/photo-1579930700019-f5f6ba3db867?q=80&w=1176');"></div>
            <div class="hero-slide" style="background-image: url('https://images.unsplash.com/photo-1512453979798-5ea266f8880c?q=80&w=1200');"></div>
            <div class="hero-slide" style="background-image: url('https://images.unsplash.com/photo-1687754715959-41fed2161528?q=80&w=1221');"></div>
        </div>
        <div class="hero-overlay"></div>
        <div class="hero-content-container">
            <div class="hero-left-content">
                <div class="hero-main-title">{hero_title}</div>
                <div class="hero-description">{hero_desc}</div>
                <div class="hero-btn-group">
                    <a href="?action=start_chat" target="_self" class="btn-dynamic-chat">{hero_btn1}</a>
                    <a href="#verified-library" class="btn-browse-library">{hero_btn2}</a>
                </div>
            </div>
        </div>
    </div>
    """)

  

    # ─────────────────────────────────────────────
    # CHAT + SIDEBAR PANEL
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

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("sources") and msg["role"] == "assistant":
                    st.markdown(t["verify_source"])
                    for src in msg["sources"]:
                        st.markdown(
                            f'<a href="{src.get("official_url","")}" target="_blank" '
                            f'style="font-size:12px; color:#0F5A41;">📎 {src.get("title","")}</a>',
                            unsafe_allow_html=True,
                        )

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
        disclaimer_text = "هذا الموقع نموذج أولي مستقل للذكاء الاصطناعي. إنه ليس بوابة حكومية إماراتية رسمية. تحقق دائماً من المصادر الرسمية." if is_arabic else "This website is an independent AI prototype. It is NOT an official UAE government portal. Always verify regulations on official gov source links."
        st.html(f"""
        <div class="side-disclaimer">
            <div class="side-disclaimer-icon">🛈</div>
            <div class="side-disclaimer-text">
                <strong>{"إخلاء مسؤولية" if is_arabic else "Prototype Disclaimer"}:</strong> {disclaimer_text}
            </div>
        </div>
        <div class="side-panel">
            <div class="panel-title">🗂️ {"روابط التحقق الرسمية" if is_arabic else "Trusted Verification Hubs"}</div>
            <a href="https://u.ae"           target="_blank" class="hub-link-item"><span>{"البوابة الرسمية للإمارات" if is_arabic else "Official UAE Portal"}</span><span>↗</span></a>
            <a href="https://icp.gov.ae"     target="_blank" class="hub-link-item"><span>{"بوابة الهوية والجنسية" if is_arabic else "ICP National Portal"}</span><span>↗</span></a>
            <a href="https://gdrfad.gov.ae"  target="_blank" class="hub-link-item"><span>{"الإقامة والجنسية دبي" if is_arabic else "GDRFA Dubai Services"}</span><span>↗</span></a>
            <a href="https://rta.ae"         target="_blank" class="hub-link-item"><span>{"هيئة الطرق والمواصلات" if is_arabic else "RTA Traffic Portal"}</span><span>↗</span></a>
            <a href="https://mohre.gov.ae"   target="_blank" class="hub-link-item"><span>{"وزارة الموارد البشرية" if is_arabic else "MOHRE Labour Agency"}</span><span>↗</span></a>
        </div>
        """)

    # ─────────────────────────────────────────────
    # VERIFIED SERVICES LIBRARY
    # ─────────────────────────────────────────────
    st.html('<div id="verified-library"></div>')
    st.html('<div class="library-wrapper">')

    lib_header_left, lib_header_right = st.columns([3, 2])

    with lib_header_left:
        st.html(f'<div class="library-title">📚 {"مكتبة الخدمات الموثّقة" if is_arabic else "Verified Services Library"} ({st.session_state.selected_library_filter})</div>')
        st.html(f'<p style="font-size:13px; color:#6B7280; margin-top:4px; margin-bottom:0;">{"تحقق من المعايير والقوائم والرسوم وأوقات الانتظار." if is_arabic else "Verify criteria, checklists, fee lists, and wait times."}</p>')

    with lib_header_right:
        filter_options = ["All", "Visa Services", "Driving License", "Business License"]
        try:
            current_index = filter_options.index(st.session_state.selected_library_filter)
        except ValueError:
            current_index = 0

        selected_option = st.selectbox(
            label="Filter",
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
            "eligibility": "Students aged 18+ studying in an accredited UAE university or college, sponsored by parent or institution.",
            "checklist": "<strong>Primary documents:</strong><br>• Official admission letter<br>• Valid passport copy<br>• Medical fitness certificate<br>• Health insurance details",
            "timeline": "🕒 10 to 15 working days.",
            "fees": "Registration: AED 150. Visa issuance: AED 100/year. Medical test: AED 250."
        },
        {
            "category": "Driving License",
            "title": "Convert Foreign Driving License to UAE",
            "badge": "Conversions",
            "badge_bg": "#ECFDF5", "badge_color": "#047857",
            "eligibility": "Holders of a valid license from approved countries (GCC, UK, US, Canada, EU, Japan, Singapore, Australia) with a valid UAE residence visa.",
            "checklist": "<strong>Primary documents:</strong><br>• Valid foreign driving license<br>• Certified translation<br>• Valid Emirates ID<br>• Eye test clearance",
            "timeline": "🕒 Same-day service.",
            "fees": "File opening: AED 200. License issuance: AED 600. Knowledge fee: AED 20."
        },
        {
            "category": "Visa Services",
            "title": "UAE Golden Visa Eligibility",
            "badge": "Golden Visa",
            "badge_bg": "#F5F3FF", "badge_color": "#6D28D9",
            "eligibility": "Real estate investors (AED 2M+), entrepreneurs (AED 500k+), highly skilled professionals, scientists, doctors, and outstanding students.",
            "checklist": "<strong>Primary documents:</strong><br>• Property title deed<br>• Accredited degree<br>• Recommendation letters<br>• Audit reports",
            "timeline": "🕒 7 to 10 working days.",
            "fees": "Nomination: AED 150. 10-year visa: AED 2,800. Emirates ID: AED 1,000."
        },
        {
            "category": "Driving License",
            "title": "UAE Driving License Renewal",
            "badge": "Renewals",
            "badge_bg": "#FFFBEB", "badge_color": "#B45309",
            "eligibility": "All residents and citizens with an active or expired UAE driving license.",
            "checklist": "<strong>Primary documents:</strong><br>• Valid Emirates ID<br>• Current/expired license<br>• Eye test record",
            "timeline": "🕒 3 to 5 working days; digital version immediate.",
            "fees": "Age 21+: AED 300. Under 21: AED 100. Eye test: AED 150–180. Courier: AED 25."
        },
        {
            "category": "Business License",
            "title": "Dubai Virtual Company License",
            "badge": "Formation",
            "badge_bg": "#FEF2F2", "badge_color": "#B91C1C",
            "eligibility": "Global business owners and non-residents from 100+ approved countries in creative, tech, and services sectors.",
            "checklist": "<strong>Primary documents:</strong><br>• Valid passport<br>• Global residency proof<br>• Background screening",
            "timeline": "🕒 25 to 30 working days.",
            "fees": "1-year license: USD 233 (AED 850). Registry fee: USD 100."
        }
    ]

    filtered_items = [
        item for item in all_library_items
        if st.session_state.selected_library_filter == "All" or item["category"] == st.session_state.selected_library_filter
    ]

    table_rows = []
    for item in filtered_items:
        table_rows.append(
            f"<tr>"
            f"<td style='width:22%;'><strong style='color:#111827; font-size:14.5px; display:block; margin-bottom:8px;'>{item['title']}</strong>"
            f"<span class='table-badge' style='background:{item['badge_bg']}; color:{item['badge_color']};'>{item['badge']}</span></td>"
            f"<td style='width:23%; color:#374151;'>{item['eligibility']}</td>"
            f"<td style='width:23%; color:#374151;'>{item['checklist']}</td>"
            f"<td style='width:14%; color:#4B5563; font-weight:500;'>{item['timeline']}</td>"
            f"<td style='width:18%; color:#111827; font-weight:600; text-align:right;'>{item['fees']}</td>"
            f"</tr>"
        )

    table_rows_html = "".join(table_rows) if table_rows else "<tr><td colspan='5' style='text-align:center; padding:40px; color:#9CA3AF;'>No records found.</td></tr>"

    st.html(
        "<div class='custom-table-container'>"
        "<table class='custom-table'><thead><tr>"
        "<th style='width:22%;'>Service Title</th>"
        "<th style='width:23%;'>Eligibility</th>"
        "<th style='width:23%;'>Required Documents</th>"
        "<th style='width:14%;'>Timeline</th>"
        "<th style='width:18%; text-align:right;'>Fees</th>"
        "</tr></thead>"
        f"<tbody>{table_rows_html}</tbody>"
        "</table></div>"
    )

    st.html("</div>")  # close library-wrapper

    # ─────────────────────────────────────────────
    # FOOTER
    # ─────────────────────────────────────────────
    st.html("""
    <div class="custom-footer-bar">
        © 2026 UAE Government Services Assistant · Hackathon Prototype · Not affiliated with any UAE government authority
    </div>
    """)


