# agents/planner.py
from core.state import AgentState

class PlannerAgent:
    @staticmethod
    def process(state: AgentState) -> AgentState:
        state['retry_count'] = 0
        return state