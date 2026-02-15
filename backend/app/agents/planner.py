from app.core.state import AgentState

def planner(state: AgentState):
    """Initialize retry counter"""
    state['retry_count'] = 0
    return state