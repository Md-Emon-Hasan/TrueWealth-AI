# agents/executor.py
from core.state import AgentState

class ExecutorAgent:
    @staticmethod
    def process(state: AgentState) -> AgentState:
        state['retry_count'] += 1
        return state