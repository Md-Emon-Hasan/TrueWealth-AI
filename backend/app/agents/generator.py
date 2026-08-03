from app.core.state import AgentState
from app.tools.llm_client import extract_tokens
from app.tools.model_gateway import get_llm


def generate_response(state: AgentState):
    """Generate final answer"""
    if state.get('source') == 'llm_knowledge':
        return state

    if state.get('documents'):
        llm = get_llm("answer")
        content = "\n".join(doc.page_content for doc in state['documents'])

        prompt = f"""You are a trusted and insightful AI-powered financial advisor assisting a client with \
financial decisions.

Conversation Context:
{''.join(state.get('conversation_history', [])[-3:])}

Client's Question:
{state['question']}

Relevant Financial Information:
{content}

Guidelines:
1. Respond in 2–3 professional, concise sentences.
2. Do not mention sources, tools, or uncertainty.
"""

        message = llm.invoke(prompt)
        res = message.content
        state['generation'] = res.strip()
        state['conversation_history'] += [f"Advisor: {res.strip()}"]
        state['tokens_used'] = state.get('tokens_used', 0) + extract_tokens(message)
        state['model_used'] = message.model_used or state.get('model_used', '')
        state['fallback_used'] = state.get('fallback_used', False) or message.fallback_used
        state['degraded'] = message.degraded or state.get('degraded', '')
        return state

    # nothing retrieved, either the source has no relevant passage or a fetch degraded upstream
    state['generation'] = "I couldn't find enough financial data to provide a confident answer right now."
    state['conversation_history'] += [state.get('generation', '')]
    state['degraded'] = state.get('degraded') or 'no_relevant_documents'
    return state
