"""
agent.py — UAE Government Services Assistant
All AI logic: knowledge base loading, TF-IDF retrieval, Gemini LLM calls.
Import this module in app.py — no Streamlit code here.
"""

import json
import os
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are Daleel, a friendly prototype AI assistant that helps residents, tourists, and people relocating to the UAE understand visa and license requirements, processes, fees, and timelines.

"Daleel" means "guide" in Arabic - which is exactly your role: a knowledgeable, trustworthy guide through UAE visa and license processes, not an official authority.

GREETING AND CONVERSATION STYLE
- When a conversation begins, greet the user warmly before diving into business. A natural UAE-style welcome works well - for example, opening with a warm "Marhaba" or "Welcome" alongside an English greeting feels appropriate, but keep it light and optional rather than a fixed script every time. You may introduce yourself as Daleel when greeting for the first time.
- Be genuinely conversational. If the user makes small talk, asks how you are, or chats casually, respond naturally and warmly before or alongside addressing their actual question.
- Reflect UAE hospitality and warmth in your tone: welcoming, respectful, patient, and generous with reassurance.
- Keep language universally comfortable for people of any nationality, background, or religion.
- Adapt formality to the user: if they're casual, be a bit more relaxed; if they write formally, match that register.

YOUR ROLE AND SCOPE
You help with questions about UAE visas (student, residence, visit/tourist, golden, green, job-seeker, dependent, renewal, cancellation, overstay, etc.) and UAE licenses (driving license, business/trade license, professional license, freelance permit, Emirates ID, and related topics).

You only answer questions within this scope. For anything clearly unrelated to UAE visas, licenses, or closely related government services (e.g. general knowledge questions, coding help, unrelated countries' immigration systems, personal advice unrelated to UAE processes), politely explain that you're focused specifically on UAE visa and license guidance and redirect the user back to that topic. Brief, friendly small talk (greetings, "how are you," thanks) is always fine and not subject to this restriction.

ANSWERING WITH THE KNOWLEDGE BASE
You will receive a "RETRIEVED CONTEXT" section with each user message, pulled from a curated knowledge base of UAE visa and license workflows. This is your primary and most trustworthy source - always prioritize it over anything else.

1. If RETRIEVED CONTEXT contains relevant information: ground your entire factual answer in it. Never invent or estimate fees, documents, timelines, or eligibility rules beyond what's given.
2. If RETRIEVED CONTEXT is empty, irrelevant, or only partially covers the question: clearly tell the user that you don't have verified details on that specific point in your current knowledge base. Do not guess or fill the gap with your own general knowledge, since you cannot verify it's current or accurate for UAE rules specifically. Instead, point them to the most relevant official UAE government source for their topic, chosen from this list:
   - General/all services: u.ae
   - Visas and Emirates ID: ICP - icp.gov.ae
   - Dubai visa services: GDRFA Dubai - gdrfad.gov.ae
   - Driving licenses: RTA - rta.ae
   - Labor/work permits: MOHRE - mohre.gov.ae
   - Business/trade licenses: DED - ded.ae
   Pick the single most relevant one for the user's specific question rather than listing all of them every time.
3. Never describe yourself as having searched, browsed, or looked something up online - you have not. You are pointing the user to where they can look it up themselves.

LANGUAGE INSTRUCTION
- You will receive a LANGUAGE INSTRUCTION in every message. Follow it strictly.
- If told to respond in Arabic, respond entirely in Arabic including all labels, steps, and source references.
- If told to respond in English, respond entirely in English.

STRICT RULES
1. Ground every factual claim in the RETRIEVED CONTEXT. Never invent fees, documents, or timelines.
2. If context is insufficient, say so clearly and direct the user to the single most relevant official source. Do not guess.
3. Always end substantive factual answers with the official source link framed as "Verify on official source: [link]" - whether that link came from the retrieved context or from the fallback list above.
4. Never claim to be an official government service or imply official affiliation.
5. Do not give legal advice or guarantee approval outcomes.
6. If the user does not meet a requirement, state this clearly and supportively, and explain the next concrete step.
7. Stay within scope (UAE visas, licenses, and closely related government services) as described above.

TONE AND STYLE
- Warm, clear, and practical.
- Use plain language; avoid jargon unless it's an official term.
- Use numbered lists for process steps.
- Do not over-elaborate. Answer what was asked, then offer to go deeper.

DISCLAIMER
If the user thinks this is an official government tool, clarify: "I'm Daleel, a prototype assistant - not an official UAE government service. Always confirm details with the official source before taking action." """

# ─────────────────────────────────────────────
# UI STRINGS — English & Arabic
# ─────────────────────────────────────────────

UI = {
    "English": {
        # Sidebar
       "config_header":     "🔑 Configuration",
        "api_label":          "Enter Google Gemini API Key",
        "api_help":           "Free-tier key from Google AI Studio.",
        "api_loaded":         "🔒 API key loaded from secrets.",
        "api_info":           "💡 Paste your Gemini API key above to begin.",
        "verify_hubs":       "### Trusted Verification Hubs",
        "clear_chat":         "🗑️ Clear Chat",
        # Disclaimer
        "disclaimer":        "⚠️ <strong>Prototype Disclaimer:</strong> This application is an independent prototype. It is <strong>NOT</strong> an official government portal. Always confirm details at the official source links provided.",
        # Nav
        "nav_logo":          "daleel",
        "nav_home":          "Home",
        "nav_visa":          "Visa Services",
        "nav_driving":       "Driving License",
        "nav_business":      "Business License",
        "nav_about":         "About",
        "toggle_btn":        "🌐 العربية",
        # Hero
        "hero_title":        "Public<br>Services Assistant",
        "hero_subtitle":     "AI-Powered Guidance for Visas, Licenses,<br>and Government Services",
        # Service cards
        "quick_services":    "Quick Services",
        "svc_visa":          "Visa Services",
        "svc_driving":       "Driving License",
        "svc_business":      "Business License",
        "svc_renewals":      "Renewals",
        "svc_faq":           "FAQs",
        # Chat section
        "chat_section":      "Main AI Chat Section",
        "quick_queries":     "⚡ Quick Queries",
        "btn_student":       "🎓 Student Visa Info",
        "btn_driving":       "🚗 Convert Driving License",
        "btn_golden":        "💼 Golden Visa Options",
        "placeholder":       "Ask about UAE visas, driving renewals, or business licenses...",
        "verify_source":     "**Verify on official source:**",
        "thinking":          "Thinking...",
        # Greeting
        "greeting":          "Marhaba! I'm Daleel 🇦🇪, your guide to UAE visas and licenses. Ask me anything about visas, driving licenses, or business licenses.",
        # Footer
        "footer":            "🏆 Hackathon Prototype · Not affiliated with any UAE government authority · Always verify at <a href='https://u.ae' target='_blank'>u.ae</a>",
        # Quick query text sent to agent
        "q_student":         "What are the requirements and process steps for a Student Visa?",
        "q_driving":         "How can I convert my foreign driving license to a UAE license?",
        "q_golden":          "What is the eligibility for a Golden Visa?",
        # Lang instruction for agent
        "lang_instruction":  "Respond in English.",
    },
    "Arabic": {
        # Sidebar
      "config_header":     "🔑 الإعدادات",
        "api_label":          "أدخل مفتاح Google Gemini API",
        "api_help":           "مفتاح مجاني من Google AI Studio.",
        "api_loaded":         "🔒 تم تحميل مفتاح API من الأسرار.",
        "api_info":           "💡 الصق مفتاح Gemini API أعلاه للبدء.",
        "verify_hubs":       "### روابط التحقق الرسمية",
        "clear_chat":         "🗑️ مسح المحادثة",
        # Disclaimer
        "disclaimer":        "⚠️ <strong>إخلاء مسؤولية:</strong> هذا التطبيق نموذج أولي مستقل. إنه <strong>ليس</strong> بوابة حكومية رسمية. يرجى دائمًا التحقق من التفاصيل عبر روابط المصادر الرسمية.",
        # Nav
        "nav_logo":          "دليل",
        "nav_home":          "الرئيسية",
        "nav_visa":          "خدمات التأشيرة",
        "nav_driving":       "رخصة القيادة",
        "nav_business":      "الرخصة التجارية",
        "nav_about":         "عن التطبيق",
        "toggle_btn":        "🌐 English",
        # Hero
        "hero_title":        "مساعد الخدمات<br>الحكومية الإماراتية",
        "hero_subtitle":     "إرشادات مدعومة بالذكاء الاصطناعي للتأشيرات<br>والتراخيص والخدمات الحكومية",
        # Service cards
        "quick_services":    "الخدمات السريعة",
        "svc_visa":          "خدمات التأشيرة",
        "svc_driving":       "رخصة القيادة",
        "svc_business":      "الرخصة التجارية",
        "svc_renewals":      "التجديدات",
        "svc_faq":           "الأسئلة الشائعة",
        # Chat section
        "chat_section":      "قسم المحادثة مع الذكاء الاصطناعي",
        "quick_queries":     "⚡ أسئلة سريعة",
        "btn_student":       "🎓 تأشيرة الطالب",
        "btn_driving":       "🚗 تحويل رخصة القيادة",
        "btn_golden":        "💼 التأشيرة الذهبية",
        "placeholder":       "اسأل عن التأشيرات أو رخص القيادة أو التراخيص التجارية...",
        "verify_source":     "**تحقق من المصدر الرسمي:**",
        "thinking":          "جارٍ التفكير...",
        # Greeting
        "greeting":          "مرحباً! أنا دليل 🇦🇪، مرشدك لتأشيرات ورخص الإمارات. اسألني عن أي شيء يتعلق بالتأشيرات أو رخص القيادة أو التراخيص التجارية.",
        # Footer
        "footer":            "🏆 نموذج أولي للهاكاثون · غير تابع لأي جهة حكومية إماراتية · تحقق دائمًا على <a href='https://u.ae' target='_blank'>u.ae</a>",
        # Quick query text sent to agent
        "q_student":         "ما هي متطلبات وخطوات الحصول على تأشيرة الطالب؟",
        "q_driving":         "كيف يمكنني تحويل رخصة القيادة الأجنبية إلى رخصة إماراتية؟",
        "q_golden":          "ما هي شروط الحصول على التأشيرة الذهبية؟",
        # Lang instruction for agent
        "lang_instruction":  "Respond entirely in Arabic (العربية). All text, steps, labels, and source references must be in Arabic.",
    },
}

# ─────────────────────────────────────────────
# KNOWLEDGE BASE
# ─────────────────────────────────────────────

def load_knowledge_base(path: str = "knowledge_base.json") -> list:
    """Load the curated KB from disk. Returns empty list if not found."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ─────────────────────────────────────────────
# RETRIEVAL
# ─────────────────────────────────────────────

def build_retrieval_index(data: list):
    """
    Build a TF-IDF index over the knowledge base.
    Returns (vectorizer, tfidf_matrix) or (None, None) if data is empty.
    """
    if not data:
        return None, None

    documents = []
    for item in data:
        blob = " ".join([
            item.get("category", ""),
            item.get("subcategory", ""),
            item.get("title", ""),
            item.get("eligibility", ""),
            str(item.get("documents", "")),
            str(item.get("steps", "")),
        ])
        documents.append(blob.lower())

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    return vectorizer, tfidf_matrix

def retrieve_context(
    query: str,
    vectorizer,
    tfidf_matrix,
    data: list,
    top_n: int = 2,
    threshold: float = 0.12,
) -> tuple[list, str]:
    """
    Find the top-n KB entries most relevant to query.
    Returns (matched_docs list, context_string for LLM prompt).
    """
    if vectorizer is None or tfidf_matrix is None:
        return [], ""

    query_vec = vectorizer.transform([query.lower()])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[::-1][:top_n]

    matched_docs = []
    context_parts = []

    for idx in top_indices:
        if similarities[idx] >= threshold:
            item = data[idx]
            matched_docs.append(item)
            context_parts.append(
                f"### {item['title']} ({item['category']}/{item['subcategory']})\n"
                f"Eligibility: {item.get('eligibility', '')}\n"
                f"Required Documents: {item.get('documents', '')}\n"
                f"Process Steps: {item.get('steps', '')}\n"
                f"Fees: {item.get('fees', '')}\n"
                f"Processing Time: {item.get('processing_time', '')}\n"
                f"Official Link: {item.get('official_url', '')}\n"
            )

    return matched_docs, "\n\n".join(context_parts)

# ─────────────────────────────────────────────
# GEMINI MODEL & CHAT SESSION
# ─────────────────────────────────────────────

def get_gemini_model(api_key: str):
    """Configure and return a Gemini GenerativeModel."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )


def start_chat_session(model):
    """Start a fresh Gemini chat session (stateful multi-turn memory)."""
    return model.start_chat(history=[])


def generate_grounded_response(
    query: str,
    context_string: str,
    chat_session,
    lang: str = "English",
) -> str:
    """
    Send a RAG-grounded message to the active chat session and return reply text.
    lang: "English" or "Arabic" — controls response language instruction.
    """
    lang_instruction = UI[lang]["lang_instruction"]

    try:
        full_message = (
            f"LANGUAGE INSTRUCTION: {lang_instruction}\n\n"
            f"RETRIEVED CONTEXT:\n{context_string or '(none found for this message)'}\n\n"
            f"USER QUESTION:\n{query}"
        )
        response = chat_session.send_message(full_message)
        return response.text
    except Exception as e:
        error = str(e)
        
        # Self-healing Cache Invalidation logic for Streamlit
        if "404" in error or "not found" in error.lower():
            try:
                import streamlit as st
                # Purge Streamlit's RAM Cache globally
                st.cache_resource.clear()
                st.cache_data.clear()
                # Remove stale states so they're cleanly recreated on refresh
                if "chat_session" in st.session_state:
                    del st.session_state["chat_session"]
                if "messages" in st.session_state:
                    st.session_state["messages"] = []
            except Exception:
                pass
            
            if lang == "Arabic":
                return (
                    "⚠️ **تم الكشف عن جلسة عمل منتهية الصلاحية (تم مسح التخزين المؤقت تلقائياً)**\n\n"
                    "لقد أوقفت Google دعم نموذج `gemini-1.5-flash`. لقد قمنا بتحديث النظام ومسح الذاكرة المؤقتة لضمان استقرار العمل.\n\n"
                    "يرجى **تحديث صفحة المتصفح الآن** لتنشيط النموذج المستقر الجديد `gemini-2.5-flash`."
                )
            return (
                "⚠️ **Stale Chat Session Detected (Cache Cleared Automatically)**\n\n"
                "Google has retired the legacy `gemini-1.5-flash` model. We have automatically cleared the global cache.\n\n"
                "Please **refresh your browser page now** to initialize the active, stable `gemini-2.5-flash` model."
            )
            
        if "429" in error or "quota" in error.lower():
            if lang == "Arabic":
                return (
                    "⚠️ **تم الوصول إلى الحد اليومي لطلبات API.**\n\n"
                    "يُرجى المحاولة لاحقاً أو التحقق مباشرة من:\n"
                    "- [u.ae](https://u.ae)\n"
                    "- [icp.gov.ae](https://icp.gov.ae)"
                )
            return (
                "⚠️ **API quota reached for today.**\n\n"
                "Please try again later or verify directly at:\n"
                "- [u.ae](https://u.ae)\n"
                "- [icp.gov.ae](https://icp.gov.ae)"
            )
        return f"Something went wrong: {error}"
