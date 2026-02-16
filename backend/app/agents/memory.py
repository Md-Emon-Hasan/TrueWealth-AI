from app.core.config import MEMORY_LIMIT
from app.core.state import AgentState


def recall_memory(state: AgentState) -> AgentState:
    """Recall last interactions from memory"""
    state['conversation_history'] = state.get('memory', [])[-MEMORY_LIMIT:]
    return state


def store_memory(state: AgentState):
    """Store conversation history to memory"""
    state['memory'] = state.get('conversation_history', [])
    return state
