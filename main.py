from ingestion.pdf_loader import load_pdf
from retrieval.splitter import split_docs
from retrieval.vectorstore import build_vectorstore
from retrieval.retrievers import get_retriever
from agents.workflow import create_workflow
from logger import logger

logger.info("Starting Financial Advisor Bot")
docs = load_pdf("data/The Intelligent Investor - BENJAMIN GRAHAM.pdf")
splits = split_docs(docs)
vs = build_vectorstore(splits)
retriever = get_retriever(vs)
app = create_workflow(retriever)

conversation_state = {
    "question": "",
    "documents": [],
    "generation": "",
    "source": "",
    "search_query": None,
    "conversation_history": [],
    "llm_attempted": False,
    "rag_attempted": False,
    "yfinance_attempted": False,
    "ddg_attempted": False,
    "retry_count": 0,
    "memory": []
}

while True:
    query = input("Client: ").strip()
    if query.lower() == "exit":
        logger.info("Session ended by user.")
        break

    conversation_state.update({
        "question": query,
        "generation": "",
        "documents": [],
        "source": "",
        "retry_count": 0
    })

    result = app.invoke(conversation_state)
    conversation_state.update(result)

    print(f"Consultant: {conversation_state['generation']}")