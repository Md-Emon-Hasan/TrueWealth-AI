# tools/llm_client.py
from langchain_groq import ChatGroq

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2048
        )
    return _llm