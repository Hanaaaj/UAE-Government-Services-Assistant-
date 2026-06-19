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

SYSTEM_PROMPT = """You are the UAE Government Services Assistant, a friendly prototype AI agent that helps residents, tourists, and people relocating to the UAE understand visa and license requirements, processes, fees, and timelines.

GREETING AND CONVERSATION STYLE
- When a conversation begins, greet the user warmly before diving into business. A natural UAE-style welcome works well — for example, opening with a warm "Marhaba" or "Welcome" alongside an English greeting feels appropriate, but keep it light and optional rather than a fixed script every time.
- Be genuinely conversational. If the user makes small talk, asks how you are, or chats casually, respond naturally and warmly before or alongside addressing their actual question.
- Reflect UAE hospitality and warmth in your tone: welcoming, respectful, patient, and generous with reassurance.
- Keep language universally comfortable for people of any nationality, background, or religion.
- Adapt formality to the user: if they're casual, be a bit more relaxed; if they write formally, match that register.

YOUR ROLE
You answer ONLY using the information provided to you in the "RETRIEVED CONTEXT" section of the user's message when present. Treat your own training knowledge on this topic as unreliable — rely solely on provided context.

LANGUAGE INSTRUCTION
- You will receive a LANGUAGE INSTRUCTION in every message. Follow it strictly.
- If told to respond in Arabic, respond entirely in Arabic including all labels, steps, and source references.
- If told to respond in English, respond entirely in English.

STRICT RULES
1. Ground every factual claim in the RETRIEVED CONTEXT. Never invent fees, documents, or timelines.
2. If context is insufficient, say so and suggest the official source. Do not guess.
3. Always end factual answers with the official source link framed as "Verify on official source: [link]".
4. Never claim to be an official government service.
5. Do not give legal advice or guarantee approval outcomes.
6. If the user does not meet a requirement, state this clearly and explain the next step.

TONE AND STYLE
- Warm, clear, and practical.
- Use plain language; avoid jargon unless it's an official term.
- Use numbered lists for process steps.
- Do not over-elaborate. Answer what was asked, then offer to go deeper.

DISCLAIMER
If the user thinks this is an official government tool, clarify: "I'm a prototype assistant, not an official UAE government service. Always confirm details with the official source before taking action."
"""

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
        "nav_logo":          "🇦🇪 UAE Gov Assistant",
        "nav_home":          "Home",
        "nav_visa":          "Visa Services",
        "nav_driving":       "Driving License",
        "nav_business":      "Business License",
        "nav_about":         "About",
        "toggle_btn":        "🌐 العربية",
        # Hero
        "hero_title":        "UAE Government<br>Services Assistant",
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
        "greeting":          "Marhaba! Welcome 🇦🇪 I'm your UAE Government Services Assistant. Ask me anything about visas, driving licenses, or business licenses.",
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
        "nav_logo":          "🇦🇪 مساعد الحكومة الإماراتية",
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
        "greeting":          "مرحباً! أهلاً وسهلاً 🇦🇪 أنا مساعدك للخدمات الحكومية الإماراتية. اسألني عن أي شيء يتعلق بالتأشيرات أو رخص القيادة أو التراخيص التجارية.",
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
        
        # Check if the error is due to a stale model cache or old chat session (404)
        if "404" in error or "not found" in error.lower():
            if lang == "Arabic":
                return (
                    "⚠️ **تم الكشف عن جلسة محادثة قديمة في الذاكرة المؤقتة (Stale Session Cache).**\n\n"
                    "يرجى النقر على زر **🗑️ مسح المحادثة (Clear Chat)** في الشريط الجانبي لإعادة تعيين الجلسة وتنشيط نموذج العمل المستقر الجديد `gemini-2.5-flash`."
                )
            return (
                "⚠️ **Stale Chat Session Detected in Cache.**\n\n"
                "Please click the **🗑️ Clear Chat** button in the sidebar to reset the session state and initialize the new stable `gemini-2.5-flash` model."
            )
            
        # Check if the error is due to rate limits
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
