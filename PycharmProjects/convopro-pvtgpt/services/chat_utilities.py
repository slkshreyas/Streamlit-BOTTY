# services/chat_utilities.py
from datetime import datetime
import pytz
from llm_factory.get_llm import get_gemini_llm


def get_current_datetime() -> dict:
    """Returns real current date/time in IST."""
    IST = pytz.timezone("Asia/Kolkata")
    now = datetime.now(IST)
    return {
        "day": now.strftime("%A"),
        "date": now.strftime("%d %B %Y"),
        "month": now.strftime("%B"),
        "year": str(now.year),
        "time": now.strftime("%I:%M %p"),
        "full": now.strftime("%A, %d %B %Y, %I:%M %p IST"),
    }


def get_answer(model_name: str, chat_history: list) -> str:
    llm = get_gemini_llm(model_name)
    dt = get_current_datetime()

    # Build history excluding last message
    gemini_history = []
    for msg in chat_history[:-1]:
        gemini_role = "model" if msg["role"] == "assistant" else "user"
        gemini_history.append({
            "role": gemini_role,
            "parts": [msg["content"]]
        })

    # Force date into every single message — cannot be ignored
    last_message = chat_history[-1]["content"]

    forced_message = f"""
##ABSOLUTE SYSTEM OVERRIDE — HIGHEST PRIORITY##
Your training data dates are WRONG and OUTDATED. IGNORE all dates from your training.
Use ONLY these REAL values provided by the live server right now:

TODAY'S DATE    : {dt['date']}
DAY OF WEEK     : {dt['day']}
CURRENT MONTH   : {dt['month']}
CURRENT YEAR    : {dt['year']}
CURRENT TIME    : {dt['time']} IST
FULL DATETIME   : {dt['full']}
REGION          : India (IST, UTC+5:30)

RULES YOU MUST FOLLOW:
- The year is {dt['year']}. NOT 2024. NOT 2023. It is {dt['year']}.
- If asked about today/current date/time/day → use ONLY the values above
- If asked about recent/current events → acknowledge your training may be outdated
- NEVER say "as of my knowledge" for date/time — you have the REAL date above
- For sports/news/events → use the real year {dt['year']} as reference

##END SYSTEM OVERRIDE##

User message: {last_message}
""".strip()

    chat = llm.start_chat(history=gemini_history)
    response = chat.send_message(forced_message)
    return response.text