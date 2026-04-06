# services/get_title.py
# Generates a short chat title using Gemini based on the first user message

from llm_factory.get_llm import get_gemini_llm


def get_chat_title(model: str, user_query: str) -> str:
    """
    Uses Gemini to generate a short title (max 6 words) for the conversation.
    Falls back to first 5 words of query if Gemini fails.
    """
    try:
        llm = get_gemini_llm(model)
        prompt = (
            "Generate a short title with maximum 6 words, no punctuation, no quotes "
            f"that summarizes this message: {user_query}\n\nTitle:"
        )
        response = llm.generate_content(prompt)
        title = response.text.strip()

        # Safety check: if too long or empty, use first 5 words of query
        words = title.split()
        if len(words) > 8 or len(title) < 2:
            return " ".join(user_query.split()[:5])
        return title

    except Exception:
        # Fallback: use first 5 words of the user query
        return " ".join(user_query.split()[:5]) or "New Chat"
