from langchain_groq import ChatGroq
from app.core.config import LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS

def get_llm():
    """Get LLM instance"""
    return ChatGroq(
        model_name=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS
    )