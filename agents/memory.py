# agents/memory.py
from core.state import AgentState

class MemoryRecallAgent:
    @staticmethod
    def process(state: AgentState) -> AgentState:
        state['conversation_history'] = state.get('memory', [])[-10:]
        return state