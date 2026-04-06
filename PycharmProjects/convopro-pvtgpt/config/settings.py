from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GEMINI_MODELS: str = "gemini-2.5-pro-preview-03-25,gemini-2.0-flash,gemini-2.0-flash-lite,gemini-1.5-flash-latest"
    SQLITE_DB_PATH: str = "convopro.db"
    APP_USERS: str = "admin:admin123,shreyas:123"  # username:password pairs

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
