from app.agents.compliance_officer_agent import compliance_officer_agent
from app.agents.duckduckgo import retrieve_duckduckgo
from app.agents.generator import generate_response
from app.agents.llm import query_llm
from app.agents.memory import recall_memory, store_memory
from app.agents.rag import retrieve_docs
from app.agents.yfinance import retrieve_yfinance
from app.core.state import AgentState
from langgraph.graph import END, StateGraph


def decide_next_step(state: AgentState) -> str:
    if state.get('llm_attempted') and "I don't know" not in state.get('generation', ''):
        return "compliance_officer_agent"

    if state.get('retry_count', 0) == 0:
        return "retrieve_docs"
    elif state.get('retry_count', 0) == 1:
        return "retrieve_yfinance"
    elif state.get('retry_count', 0) == 2:
        return "retrieve_duckduckgo"
    else:
        return "generate_response"


def get_workflow_app():
    workflow = StateGraph(AgentState)

    # Define nodes
    workflow.add_node("recall_memory", recall_memory)
    workflow.add_node("query_llm", query_llm)
    workflow.add_node("retrieve_docs", retrieve_docs)
    workflow.add_node("retrieve_yfinance", retrieve_yfinance)
    workflow.add_node("retrieve_duckduckgo", retrieve_duckduckgo)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("compliance_officer_agent", compliance_officer_agent)
    workflow.add_node("store_memory", store_memory)

    # Define edges
    workflow.set_entry_point("recall_memory")
    workflow.add_edge("recall_memory", "query_llm")

    workflow.add_conditional_edges(
        "query_llm",
        decide_next_step,
        {
            "compliance_officer_agent": "compliance_officer_agent",
            "retrieve_docs": "retrieve_docs",
            "retrieve_yfinance": "retrieve_yfinance",
            "retrieve_duckduckgo": "retrieve_duckduckgo",
            "generate_response": "generate_response"
        }
    )

    # Continue from tools back to LLM or directly to Generate if needed
    workflow.add_edge("retrieve_docs", "generate_response")
    workflow.add_edge("retrieve_yfinance", "generate_response")
    workflow.add_edge("retrieve_duckduckgo", "generate_response")

    # every path converges through compliance before anything is stored or returned
    workflow.add_edge("generate_response", "compliance_officer_agent")
    workflow.add_edge("compliance_officer_agent", "store_memory")
    workflow.add_edge("store_memory", END)

    return workflow.compile()
