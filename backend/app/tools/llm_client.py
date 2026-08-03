import os

from langchain_groq import ChatGroq


def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )


def extract_tokens(message):
    """Best-effort token count from a ChatGroq response, 0 if the provider omits usage"""
    try:
        return message.response_metadata.get("token_usage", {}).get("total_tokens", 0) or 0
    except AttributeError:
        return 0
