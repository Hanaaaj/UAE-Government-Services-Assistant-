"""
app.py — UAE Government Services Assistant
Pure Streamlit UI. All AI/retrieval logic lives in agent.py.
"""

import base64
import streamlit as st

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
)

# ─────────────────────────────────────────────
# LANGUAGE STATE  (must be before any UI render)
# ─────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "English"

t = UI[st.session_state.lang]          # shorthand — use t["key"] everywhere
is_arabic = st.session_state.lang == "Arabic"

# ─────────────────────────────────────────────
# CSS  (base + conditional RTL/Arabic font)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

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
.nav-logo  { font-size: 22px; font-weight: 700; color: #006C4C; }
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
.service-card:hover  { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
.service-card.active { background: #FFF7E6; border-color: #D4AF37; }
.service-card .icon  { font-size: 30px; margin-bottom: 8px; }
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
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# RTL + Cairo font when Arabic is active
if is_arabic:
    st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    .nav-bar  { flex-direction: row-reverse; }
    .nav-links { flex-direction: row-reverse; }
    .disclaimer { border-left: none; border-right: 6px solid #ffc107; }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def img_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ─────────────────────────────────────────────
# AGENT RESOURCES  (cached)
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
    st.header(t["config_header"])

    if "GEMINI_API_KEY" in st.secrets:
        api_key_input = st.secrets["GEMINI_API_KEY"]
        st.success(t["api_loaded"])
    else:
        api_key_input = st.text_input(
            t["api_label"],
            type="password",
            help=t["api_help"],
        )
        if not api_key_input:
            st.info(t["api_info"])

    st.markdown("---")
    st.markdown(t["verify_hubs"])
    st.markdown("- [Official UAE Portal](https://u.ae)")
    st.markdown("- [ICP Portal](https://icp.gov.ae)")
    st.markdown("- [GDRFA Portal](https://gdrfad.gov.ae)")
    st.markdown("- [RTA Portal](https://rta.ae)")
    st.markdown("- [MOHRE Portal](https://mohre.gov.ae)")

    st.markdown("---")
    if st.button(t["clear_chat"]):
        st.session_state.messages = []
        st.session_state.pop("chat_session", None)
        st.rerun()

# ─────────────────────────────────────────────
# DISCLAIMER
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="disclaimer">{t["disclaimer"]}</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# NAV BAR  +  LANGUAGE TOGGLE (top right)
# ─────────────────────────────────────────────
nav_col, toggle_col = st.columns([11, 1])

with toggle_col:
    st.markdown("<div style='padding-top:8px'>", unsafe_allow_html=True)
    if st.button(t["toggle_btn"], key="lang_toggle"):
        st.session_state.lang = "Arabic" if st.session_state.lang == "English" else "English"
        st.session_state.pop("chat_session", None)   # reset chat on lang switch
        st.session_state.messages = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with nav_col:
    st.markdown(f"""
    <div class="nav-bar">
        <div class="nav-logo">{t["nav_logo"]}</div>
        <div class="nav-links">
            <span>{t["nav_home"]}</span>
            <span>{t["nav_visa"]}</span>
            <span>{t["nav_driving"]}</span>
            <span>{t["nav_business"]}</span>
            <span>{t["nav_about"]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
try:
    hero_enc = img_to_b64("hero_banner2.png")
    text_side = "right: 6%" if is_arabic else "left: 6%"
    st.markdown(f"""
    <div style="position:relative; width:100%; border-radius:25px; overflow:hidden; margin-bottom:28px;">
        <img src="data:image/png;base64,{hero_enc}" style="width:100%; border-radius:25px;">
        <div style="position:absolute; top:18%; {text_side}; color:black; max-width:60%;">
            <div style="font-size:42px; font-weight:800; line-height:1.05; margin-bottom:10px;">
                {t["hero_title"]}
            </div>
            <div style="font-size:18px; font-weight:500; line-height:1.3; color:#111;">
                {t["hero_subtitle"]}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#006C4C,#004d35);
                border-radius:25px; padding:50px 40px; margin-bottom:28px; color:white;">
        <div style="font-size:38px; font-weight:800; margin-bottom:10px;">
            🇦🇪 {t["hero_title"].replace('<br>', ' ')}
        </div>
        <div style="font-size:17px; opacity:0.9;">{t["hero_subtitle"].replace('<br>', ' ')}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# QUICK SERVICE CARDS
# ─────────────────────────────────────────────
st.markdown(
    f"<div style='font-size:22px; font-weight:700; color:#1E293B; margin-bottom:14px;'>{t['quick_services']}</div>",
    unsafe_allow_html=True,
)

services = [
    ("🛂", t["svc_visa"],     True),
    ("🚗", t["svc_driving"],  False),
    ("🏢", t["svc_business"], False),
    ("🔄", t["svc_renewals"], False),
    ("❓", t["svc_faq"],      False),
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
# SERVICE BANNER (optional second image)
# ─────────────────────────────────────────────
try:
    svc_enc = img_to_b64("service_banner1.png")
    st.markdown(f"""
    <div style="position:relative; width:100%; border-radius:20px; overflow:hidden; margin-bottom:24px;">
        <img src="data:image/png;base64,{svc_enc}" style="width:100%; display:block;">
        <div style="position:absolute; top:10%; left:50%; transform:translateX(-50%);
                    padding:10px 20px; border-radius:12px; white-space:nowrap;">
            <h2 style="color:black; margin:0; font-size:26px; font-weight:700;">{t["chat_section"]}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown("---")
    st.markdown(f"### 💬 {t['chat_section']}")

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if api_key_input and "chat_session" not in st.session_state:
    model = _get_model(api_key_input)
    st.session_state.chat_session = start_chat_session(model)

# Static greeting (saves 1 API call per session)
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": t["greeting"],
        "sources": [],
    })

# ─────────────────────────────────────────────
# QUICK QUERY BUTTONS
# ─────────────────────────────────────────────
st.markdown(f"### {t['quick_queries']}")
q_col1, q_col2, q_col3 = st.columns(3)
quick_query = None

with q_col1:
    if st.button(t["btn_student"]):
        quick_query = t["q_student"]
with q_col2:
    if st.button(t["btn_driving"]):
        quick_query = t["q_driving"]
with q_col3:
    if st.button(t["btn_golden"]):
        quick_query = t["q_golden"]

if quick_query and api_key_input:
    matched_docs, context_string = retrieve_context(quick_query, vectorizer, tfidf_matrix, kb_data)
    reply = generate_grounded_response(
        quick_query, context_string, st.session_state.chat_session,
        lang=st.session_state.lang,
    )
    st.session_state.messages.append({"role": "user",      "content": quick_query, "sources": []})
    st.session_state.messages.append({"role": "assistant", "content": reply, "sources": matched_docs})
    st.rerun()

# ─────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources") and msg["role"] == "assistant":
            st.markdown(t["verify_source"])
            for src in msg["sources"]:
                st.markdown(
                    f'<a href="{src["official_url"]}" target="_blank" class="source-badge">'
                    f'📎 {src["title"]}</a>',
                    unsafe_allow_html=True,
                )

# ─────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────
if user_input := st.chat_input(t["placeholder"]):
    if not api_key_input:
        st.warning(t["api_info"])
    else:
        st.session_state.messages.append({"role": "user", "content": user_input, "sources": []})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            matched_docs, context_string = retrieve_context(
                user_input, vectorizer, tfidf_matrix, kb_data
            )
            with st.spinner(t["thinking"]):
                reply = generate_grounded_response(
                    user_input, context_string, st.session_state.chat_session,
                    lang=st.session_state.lang,
                )
                st.write(reply)
                if matched_docs:
                    st.markdown(t["verify_source"])
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
    f"<div style='text-align:center; font-size:0.78rem; color:#999;'>{t['footer']}</div>",
    unsafe_allow_html=True,
)
