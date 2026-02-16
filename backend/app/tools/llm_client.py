import os

from langchain_groq import ChatGroq


def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
