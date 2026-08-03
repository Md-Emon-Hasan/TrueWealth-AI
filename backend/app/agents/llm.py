from app.core.state import AgentState
from app.tools.llm_client import extract_tokens, get_llm


def query_llm(state: AgentState):
    """Initial attempt with LLM knowledge"""
    llm = get_llm()
    ctx = "\n".join(state['conversation_history'])

    prompt = f"""You are a trusted, knowledgeable, and insightful AI-powered financial advisor.

Client's Financial History & Discussion:
{ctx}

Client's Query:
{state['question']}

Respond like an experienced financial advisor in 2–3 sentences. Be professional, concise, and confident. \
Avoid mentioning data sources or expressing uncertainty."""

    message = llm.invoke(prompt)
    res = message.content

    state['conversation_history'] += [
        f"Client: {state['question']}",
        f"Advisor: {res.strip()}"
    ]

    state.update({
        "generation": res.strip(),
        "source": "llm_knowledge",
        "llm_attempted": True,
        "tokens_used": state.get('tokens_used', 0) + extract_tokens(message)
    })

    return state
