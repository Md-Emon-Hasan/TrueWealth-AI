from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.workflow import create_workflow
from ingestion.pdf_loader import load_pdf
from retrieval.splitter import split_docs
from retrieval.vectorstore import build_vectorstore
from retrieval.retrievers import get_retriever
from logger import logger
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Load documents once during startup
docs = load_pdf("data/The Intelligent Investor - BENJAMIN GRAHAM.pdf")
splits = split_docs(docs)
vs = build_vectorstore(splits)
retriever = get_retriever(vs)
advisor_bot = create_workflow(retriever)

# Pydantic models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    response: str
    conversation_history: list

# Endpoint
@app.post("/ask/", response_model=QueryResponse)
async def get_advice(request: QueryRequest):
    conversation_state = {
        "question": request.question,
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

    try:
        result = advisor_bot.invoke(conversation_state)
        conversation_state.update(result)
        response = conversation_state['generation']
        logger.info(f"Client Question: {request.question}")
        logger.info(f"Advisor Response: {response}")
    except Exception as e:
        logger.exception("Failed to process query.")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return QueryResponse(
        question=request.question,
        response=response,
        conversation_history=conversation_state['conversation_history']
    )

# This part makes the app runnable directly with `python fastapi_app.py`
if __name__ == "__main__":
    logger.info("Starting FastAPI server on http://localhost:8000")
    uvicorn.run("fastapi_app:app", host="127.0.0.1", port=8000, reload=True)
