from app.core.config import MEMORY_LIMIT, SEMANTIC_MEMORY_TOP_K
from app.core.state import AgentState
from app.tools.vector_store import get_memory_store


def _rehydrate_from_db(session_id):
    from app.core.db import get_session_history
    try:
        rows = get_session_history(session_id, limit=MEMORY_LIMIT // 2)
    except Exception:
        return []
    history = []
    for row in rows:
        history += [f"Client: {row.question}", f"Advisor: {row.answer}"]
    return history


def _recall_semantic_memory(state):
    question = state.get('question', '')
    session_id = state.get('session_id', '')
    if not question:
        return []
    try:
        store = get_memory_store()
        docs = store.similarity_search(question, k=SEMANTIC_MEMORY_TOP_K, filter={"session_id": session_id})
        return [d.page_content for d in docs]
    except Exception:
        return []


def _store_semantic_memory(state):
    question = state.get('question', '')
    generation = state.get('generation', '')
    if not question or not generation:
        return
    try:
        store = get_memory_store()
        exchange = f"Client: {question}\nAdvisor: {generation}"
        store.add_texts([exchange], metadatas=[{"session_id": state.get('session_id', '')}])
    except Exception:
        pass


def recall_memory(state: AgentState) -> AgentState:
    """Recall last interactions from memory, rehydrating from SQLite if this process has none yet"""
    memory = state.get('memory') or _rehydrate_from_db(state.get('session_id', ''))
    state['conversation_history'] = memory[-MEMORY_LIMIT:]

    recalled = _recall_semantic_memory(state)
    if recalled:
        state['conversation_history'] = recalled + state['conversation_history']

    return state


def store_memory(state: AgentState):
    """Store conversation history to memory, short-term buffer and long-term semantic recall"""
    state['memory'] = state.get('conversation_history', [])
    _store_semantic_memory(state)
    return state
