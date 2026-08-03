import re

from app.agents.compliance_officer_agent import compliance_officer_agent
from app.agents.duckduckgo import retrieve_duckduckgo
from app.agents.due_diligence_agent import due_diligence_agent
from app.agents.generator import generate_response
from app.agents.llm import query_llm
from app.agents.market_desk_agent import market_desk_agent
from app.agents.memory import recall_memory, store_memory
from app.agents.portfolio_analyst_agent import portfolio_analyst_agent
from app.agents.rag import retrieve_docs
from app.agents.yfinance import retrieve_yfinance
from app.core.state import AgentState
from langgraph.graph import END, StateGraph

# unvalidated heuristics: uppercase 2-5 letter tokens will false-positive on acronyms like ETF/CEO/IRA
_PORTFOLIO_PATTERN = re.compile(
    r"\bmy (portfolio|holdings|allocation)\b|\bi (own|hold)\b|\bshares of\b|\brisk exposure\b|\brebalance\b", re.I
)
_MARKET_KEYWORDS = re.compile(
    r"\b(stock price|current price|trading at|share price|quote for|latest news|news (on|about))\b", re.I
)
_TICKER_PATTERN = re.compile(r"\b[A-Z]{2,5}\b")


def route_intent(state: AgentState) -> str:
    question = state.get('question', '')
    if state.get('portfolio_input') or _PORTFOLIO_PATTERN.search(question):
        return "portfolio_analyst_agent"
    if _MARKET_KEYWORDS.search(question) or _TICKER_PATTERN.search(question):
        return "market_desk_agent"
    return "query_llm"


def decide_next_step(state: AgentState) -> str:
    if state.get('llm_attempted') and "I don't know" not in state.get('generation', ''):
        return "due_diligence_agent"

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
    workflow.add_node("market_desk_agent", market_desk_agent)
    workflow.add_node("portfolio_analyst_agent", portfolio_analyst_agent)
    workflow.add_node("due_diligence_agent", due_diligence_agent)
    workflow.add_node("compliance_officer_agent", compliance_officer_agent)
    workflow.add_node("store_memory", store_memory)

    # Define edges
    workflow.set_entry_point("recall_memory")

    workflow.add_conditional_edges(
        "recall_memory",
        route_intent,
        {
            "portfolio_analyst_agent": "portfolio_analyst_agent",
            "market_desk_agent": "market_desk_agent",
            "query_llm": "query_llm",
        }
    )

    workflow.add_conditional_edges(
        "query_llm",
        decide_next_step,
        {
            "due_diligence_agent": "due_diligence_agent",
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
    workflow.add_edge("market_desk_agent", "generate_response")

    # every path converges through due diligence, then compliance, before anything is stored or returned
    workflow.add_edge("generate_response", "due_diligence_agent")
    workflow.add_edge("portfolio_analyst_agent", "due_diligence_agent")
    workflow.add_edge("due_diligence_agent", "compliance_officer_agent")
    workflow.add_edge("compliance_officer_agent", "store_memory")
    workflow.add_edge("store_memory", END)

    return workflow.compile()
