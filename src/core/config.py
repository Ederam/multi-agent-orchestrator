import os
from dotenv import load_dotenv

# Carga variables desde el archivo .env
load_dotenv()

class Settings:
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    MODEL_NAME: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.3

settings = Settings()