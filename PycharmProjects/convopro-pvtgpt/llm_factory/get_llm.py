# llm_factory/get_llm.py
import google.generativeai as genai
from config.settings import Settings

settings = Settings()

genai.configure(api_key=settings.GEMINI_API_KEY)

_current_model_name = None
_current_llm_instance = None

def get_gemini_llm(model_name: str):
    global _current_model_name, _current_llm_instance
    if _current_model_name == model_name and _current_llm_instance is not None:
        return _current_llm_instance
    llm = genai.GenerativeModel(model_name=model_name)
    _current_model_name = model_name
    _current_llm_instance = llm
    return llm