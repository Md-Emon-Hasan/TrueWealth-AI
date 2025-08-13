# medical_ai_assistant/main.py (FastAPI version)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.workflow import get_workflow_app
from core.state import initialize_state
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(
    title="Financial Advisor AI API",
    description="API for the modular financial advisor AI system",
    version="1.0.0"
)

# Initialize the workflow once at startup
workflow_app = get_workflow_app()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    source: str

# In-memory session store (replace with Redis in production)
sessions = {}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main endpoint for financial advice queries"""
    try:
        # Get or create session
        if request.session_id not in sessions:
            sessions[request.session_id] = initialize_state()
        
        state = sessions[request.session_id]
        
        # Update state with new message
        state.update({
            "question": request.message,
            "generation": "",
            "documents": [],
            "source": "",
            "retry_count": 0
        })

        # Process through workflow
        result = workflow_app.invoke(state)
        state.update(result)
        
        return ChatResponse(
            response=state["generation"],
            session_id=request.session_id,
            source=state["source"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/reset")
async def reset_session(session_id: str):
    """Reset a conversation session"""
    sessions[session_id] = initialize_state()
    return {"status": "session reset"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)