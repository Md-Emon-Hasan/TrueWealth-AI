from core.state import AgentState
from tools.llm_client import get_llm

def generate_response(state: AgentState):
    """Generate final answer"""
    if state['source'] == 'llm_knowledge':
        return state

    if state['documents']:
        llm = get_llm()
        content = "\n".join(doc.page_content for doc in state['documents'])
        
        prompt = f"""You are a trusted and insightful AI-powered financial advisor assisting a client with financial decisions.

Conversation Context:
{''.join(state['conversation_history'][-3:])}

Client's Question:
{state['question']}

Relevant Financial Information:
{content}

Guidelines:
1. Respond in 2–3 professional, concise sentences.
2. Do not mention sources, tools, or uncertainty.
"""
        
        res = llm.invoke(prompt).content
        state['generation'] = res.strip()
        state['conversation_history'] += [f"Advisor: {res.strip()}"]
        return state

    # Fallback response if nothing found
    state['generation'] = "I couldn't find enough financial data to provide a confident answer right now. Please consult a certified financial expert."
    state['conversation_history'] += [state['generation']]
    return state