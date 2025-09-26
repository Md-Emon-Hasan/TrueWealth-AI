from core.state import AgentState

def executor(state: AgentState):
    """Increment retry counter"""
    state['retry_count'] += 1
    return state