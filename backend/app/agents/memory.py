from app.core.state import AgentState
from app.core.config import MEMORY_LIMIT

def recall_memory(state: AgentState):
    """Recall last 10 interactions from memory"""
    state['conversation_history'] = state.get('memory', [])[-MEMORY_LIMIT:]
    return state

def store_memory(state: AgentState):
    """Store conversation history to memory"""
    state['memory'] = state['conversation_history']
    return state