# services/get_models_list.py
# Returns list of Gemini models from settings

from config.settings import Settings
settings = Settings()

def get_gemini_models_list() -> list:
    """Reads GEMINI_MODELS from .env and returns as a list."""
    models_str = settings.GEMINI_MODELS
    return [m.strip() for m in models_str.split(",") if m.strip()]
