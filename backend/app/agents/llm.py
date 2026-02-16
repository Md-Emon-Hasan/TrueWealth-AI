from app.core.state import AgentState
from app.tools.llm_client import get_llm


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

    res = llm.invoke(prompt).content

    state['conversation_history'] += [
        f"Client: {state['question']}",
        f"Advisor: {res.strip()}"
    ]

    state.update({
        "generation": res.strip(),
        "source": "llm_knowledge",
        "llm_attempted": True
    })

    return state
