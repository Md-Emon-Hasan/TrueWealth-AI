import uvicorn
from app.core.logger import logger
from app.core.state import initialize_state
from app.core.workflow import get_workflow_app
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()

app = FastAPI(title="TrueWealth AI API", version="2.0")

# Initialize workflow
logger.info("Initializing TrueWealth AI Workflow...")
ai_workflow = get_workflow_app()
conversation_states = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    source: str


@app.post("/api/chat", response_model=ChatResponse)
async def api_chat(request: ChatRequest):
    """API endpoint for chat"""
    try:
        user_input = request.message
        session_id = request.session_id

        if session_id not in conversation_states:
            logger.info(f"Creating new state for session: {session_id}")
            conversation_states[session_id] = initialize_state()

        state = conversation_states[session_id]

        state.update({
            "question": user_input,
            "generation": "",
            "documents": [],
            "source": "",
            "retry_count": 0
        })

        # Invoke workflow
        logger.info(f"Invoking workflow for session {session_id} with question: {user_input[:50]}...")
        result = ai_workflow.invoke(state)
        state.update(result)

        return ChatResponse(
            response=state.get('generation', ''),
            session_id=session_id,
            source=state.get('source', '')
        )
    except Exception as e:
        logger.error(f"Error in api_chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5001)
