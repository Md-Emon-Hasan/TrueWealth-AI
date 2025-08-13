# agents/memory_store.py
from core.state import AgentState

class MemoryStoreAgent:
    @staticmethod
    def process(state: AgentState) -> AgentState:
        state['memory'] = state['conversation_history']
        return state