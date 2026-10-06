from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import settings

def get_gemini_client() -> ChatGoogleGenerativeAI | None:
    """Instancia y retorna el cliente LLM de Gemini si la API Key existe."""
    if not settings.GEMINI_API_KEY:
        return None
    
    return ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=settings.TEMPERATURE
    )

# Singleton del cliente
llm_client = get_gemini_client()