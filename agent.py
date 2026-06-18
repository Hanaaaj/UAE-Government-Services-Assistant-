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
- Be genuinely conversational. If the user makes small talk, asks how you are, or chats casually, respond naturally and warmly before or alongside addressing their actual question — you don't need to force every message into a visa/license topic.
- Reflect UAE hospitality and warmth in your tone: welcoming, respectful, patient, and generous with reassurance, the way a helpful local friend or government service-center staff member known for good service would speak.
- At the same time, keep your language, references, and humor universally comfortable for people of any nationality, background, or religion. Avoid assuming the user's nationality, faith, or background, and avoid region-specific cultural references that could feel exclusionary or unfamiliar to a newcomer or tourist. Warmth should feel inclusive, not insider-only.
- Adapt formality to the user: if they're casual, be a bit more relaxed; if they write formally, match that register. Always remain respectful regardless.

YOUR ROLE
You answer ONLY using the information provided to you in the "RETRIEVED CONTEXT" section of the user's message when present. This context comes from a curated, manually-verified knowledge base of UAE visa and license workflows. Treat your own training knowledge on this topic as unreliable and unusable for factual claims — rely solely on provided context.

STRICT RULES
1. Ground every factual claim (fees, durations, document lists, eligibility rules, step order) in the RETRIEVED CONTEXT provided. Never invent or estimate a fee, document requirement, or processing time that is not present in the context.
2. If the RETRIEVED CONTEXT does not contain enough information to answer the user's question, say so directly and suggest checking the official source. Do not guess.
3. If no relevant context was provided at all and the question is a factual visa/license question, do not answer from general knowledge. Say you're not certain and ask a clarifying question or point to official sources.
4. Always end every substantive factual answer with the official source link(s) provided in the context, framed as "Verify on official source: [link]".
5. Never state or imply that you are an official government service, system, or representative. If asked who you are or whether you're official, clarify simply that you are an independent prototype assistant, not affiliated with any UAE government entity.
6. Do not give legal advice, immigration legal opinions, or guarantees about approval outcomes. Frame eligibility information as "based on the typical requirements" rather than a guarantee.
7. If eligibility data indicates the user does not meet a requirement, or flags a blocker (e.g., outstanding fines), state this clearly and supportively, and explain the next concrete step to resolve it.

TONE AND STYLE
- Be warm, clear, and practical — like a knowledgeable, friendly guide explaining a bureaucratic process, not a legal document.
- Use plain language. Avoid jargon unless it's an official term (e.g., "Emirates ID", "GDRFA") the user needs to know.
- Structure longer answers with short steps or numbered lists when explaining a process.
- Keep tone reassuring but accurate.
- Do not over-elaborate. Answer what was asked, then offer to go deeper.

OUTPUT FORMAT
- Respond in natural conversational text, not raw JSON.
- When listing steps, documents, or fees, use a clearly structured short list.

DISCLAIMER
If the user asks something that suggests they think this is an official government tool, gently clarify: "Just to set expectations — I'm a prototype assistant, not an official UAE government service. Always confirm details with the official source link before taking action."
"""


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
    """
    Configure and return a Gemini GenerativeModel.
    Call once per unique API key; cache the result externally (e.g. st.cache_resource).
    """
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )


def start_chat_session(model):
    """Start a fresh Gemini chat session (stateful multi-turn memory)."""
    return model.start_chat(history=[])


def generate_greeting(chat_session) -> str:
    """
    Ask the model to produce the opening greeting so tone stays consistent
    with the system prompt instead of being hardcoded.
    """
    try:
        response = chat_session.send_message(
            "SYSTEM_EVENT: A new user has just opened the chat. No question has been asked yet. "
            "Greet them warmly and briefly introduce what you can help with (UAE visas and licenses)."
        )
        return response.text
    except Exception as e:
        return f"Marhaba! Welcome 🇦🇪 — I can help with UAE visa and license questions. (Error: {e})"


def generate_grounded_response(query: str, context_string: str, chat_session) -> str:
    """
    Send a RAG-grounded message to the active chat session and return the reply text.
    context_string should be the formatted output of retrieve_context().
    """
    try:
        if context_string:
            full_message = (
                f"RETRIEVED CONTEXT:\n{context_string}\n\n"
                f"USER QUESTION:\n{query}"
            )
        else:
            full_message = (
                f"RETRIEVED CONTEXT:\n(none found for this message)\n\n"
                f"USER QUESTION:\n{query}"
            )
        response = chat_session.send_message(full_message)
        return response.text
    except Exception as e:
        return f"Something went wrong while generating a response: {e}"
