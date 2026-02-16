from app.core.state import AgentState


def executor(state: AgentState):
    """Increment retry counter"""
    state['retry_count'] = state.get('retry_count', 0) + 1
    return state
