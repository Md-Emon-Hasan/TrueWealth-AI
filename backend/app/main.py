import time
from typing import Literal, Optional

import uvicorn
from app.core.cache import answer_cache, cache_get, cache_set, used_live_market_data
from app.core.config import RATE_LIMIT, RATE_LIMIT_ENABLED
from app.core.db import (get_history, get_review_queue, get_stats, init_db,
                         log_query, submit_review)
from app.core.logger import logger
from app.core.review import needs_review
from app.core.state import initialize_state
from app.core.workflow import get_workflow_app
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Load environment variables
load_dotenv()

app = FastAPI(title="TrueWealth AI API", version="2.0")


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=client_key, enabled=RATE_LIMIT_ENABLED)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize workflow
logger.info("Initializing TrueWealth AI Workflow...")
ai_workflow = get_workflow_app()
init_db()
conversation_states = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    portfolio: Optional[list] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    source: str
    degraded: Optional[str] = None
    compliance: Optional[dict] = None
    verification: Optional[dict] = None
    portfolio_analysis: Optional[dict] = None


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit(RATE_LIMIT)
async def api_chat(request: Request, chat_request: ChatRequest):
    """API endpoint for chat"""
    try:
        user_input = chat_request.message
        session_id = chat_request.session_id

        cached = cache_get(answer_cache, user_input)
        if cached is not None:
            log_query(
                session_id=session_id,
                question=user_input,
                answer=cached['generation'],
                source=cached['source'],
                agents_run=["cache"],
                latency_ms=0.0,
                degraded=cached.get('degraded') or None,
                compliance_violations=(cached.get('compliance') or {}).get('violations'),
                verification_risk=(cached.get('verification') or {}).get('risk'),
                needs_review=needs_review(
                    cached.get('verification'), cached.get('compliance'),
                    cached.get('degraded'), cached['source']
                )
            )
            return ChatResponse(
                response=cached['generation'],
                session_id=session_id,
                source=cached['source'],
                degraded=cached.get('degraded') or None,
                compliance=cached.get('compliance'),
                verification=cached.get('verification')
            )

        if session_id not in conversation_states:
            logger.info(f"Creating new state for session: {session_id}")
            conversation_states[session_id] = initialize_state()

        state = conversation_states[session_id]

        state.update({
            "question": user_input,
            "generation": "",
            "documents": [],
            "source": "",
            "retry_count": 0,
            "degraded": "",
            "tokens_used": 0,
            "model_used": "",
            "fallback_used": False,
            "compliance": None,
            "verification": None,
            "portfolio_input": chat_request.portfolio,
            "portfolio_analysis": None,
            "session_id": session_id
        })

        # Invoke workflow
        logger.info(f"Invoking workflow for session {session_id} with question: {user_input[:50]}...")
        start = time.perf_counter()
        result = await ai_workflow.ainvoke(state)
        latency_ms = (time.perf_counter() - start) * 1000
        state.update(result)

        generation = state.get('generation', '')
        source = state.get('source', '')
        degraded = state.get('degraded') or None
        compliance = state.get('compliance')
        verification = state.get('verification')
        portfolio_analysis = state.get('portfolio_analysis')

        agents_run = [
            name for name, attempted in (
                ("llm", state.get('llm_attempted')),
                ("rag", state.get('rag_attempted')),
                ("yfinance", state.get('yfinance_attempted')),
                ("duckduckgo", state.get('ddg_attempted')),
                ("portfolio_analyst", source == 'portfolio_analysis'),
                ("market_desk", source == 'market_desk'),
            ) if attempted
        ]

        log_query(
            session_id=session_id,
            question=user_input,
            answer=generation,
            source=source,
            agents_run=agents_run,
            latency_ms=latency_ms,
            tokens_used=state.get('tokens_used') or None,
            degraded=degraded,
            model_used=state.get('model_used') or None,
            fallback_used=state.get('fallback_used', False),
            compliance_violations=(compliance or {}).get('violations'),
            verification_risk=(verification or {}).get('risk'),
            needs_review=needs_review(verification, compliance, degraded, source)
        )

        if not used_live_market_data(source):
            cache_set(answer_cache, user_input, {
                'generation': generation, 'source': source, 'degraded': degraded,
                'compliance': compliance, 'verification': verification
            })

        return ChatResponse(
            response=generation,
            session_id=session_id,
            source=source,
            degraded=degraded,
            compliance=compliance,
            verification=verification,
            portfolio_analysis=portfolio_analysis
        )
    except Exception as e:
        logger.error(f"Error in api_chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/history")
async def api_history(limit: int = 50, offset: int = 0):
    """Paginated query audit log"""
    rows = get_history(limit=limit, offset=offset)
    return [row.model_dump() for row in rows]


@app.get("/api/stats")
async def api_stats():
    """Aggregate stats over the query audit log"""
    return get_stats()


class ReviewSubmission(BaseModel):
    verdict: Literal["approved", "rejected", "needs_correction"]


@app.get("/api/review")
async def api_review_queue(limit: int = 50, offset: int = 0, status: str = "pending"):
    """Paginated human review queue, unauthenticated - do not expose this without auth in production"""
    rows = get_review_queue(limit=limit, offset=offset, status=status)
    return [row.model_dump() for row in rows]


@app.post("/api/review/{query_id}")
@limiter.limit(RATE_LIMIT)
async def api_submit_review(request: Request, query_id: int, submission: ReviewSubmission):
    """Records a human verdict alongside the model's original answer, never overwriting it"""
    entry = submit_review(query_id, submission.verdict)
    if entry is None:
        raise HTTPException(status_code=404, detail="query not found")
    return entry.model_dump()


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5001)
