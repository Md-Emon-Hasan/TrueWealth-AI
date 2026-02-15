from langgraph.graph import StateGraph
from langgraph.graph import END
from app.core.state import AgentState
from app.core.config import MAX_RETRY

# Import all agents
from app.agents.planner import planner
from app.agents.memory import recall_memory, store_memory
from app.agents.llm import query_llm
from app.agents.executor import executor
from app.agents.rag import retrieve_docs
from app.agents.yfinance import retrieve_yfinance
from app.agents.duckduckgo import retrieve_duckduckgo
from app.agents.generator import generate_response

def get_workflow_app():
    """Create and return compiled workflow"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner)
    workflow.add_node("recall_memory", recall_memory)
    workflow.add_node("llm_query", query_llm)
    workflow.add_node("executor", executor)
    workflow.add_node("rag_query", retrieve_docs)
    workflow.add_node("yfinance_query", retrieve_yfinance)
    workflow.add_node("ddg_query", retrieve_duckduckgo)
    workflow.add_node("generate", generate_response)
    workflow.add_node("store_memory", store_memory)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Add edges
    workflow.add_edge("planner", "recall_memory")
    workflow.add_edge("recall_memory", "llm_query")
    
    # Conditional edges
    workflow.add_conditional_edges(
        "llm_query",
        lambda s: "generate" if s.get('generation') else "executor",
        {"generate": "generate", "executor": "executor"}
    )
    
    workflow.add_conditional_edges(
        "executor",
        lambda s: "rag_query" if s['retry_count'] < MAX_RETRY else "yfinance_query",
        {"rag_query": "rag_query", "yfinance_query": "yfinance_query"}
    )
    
    workflow.add_conditional_edges(
        "rag_query",
        lambda s: "generate" if s['documents'] else "yfinance_query",
        {"generate": "generate", "yfinance_query": "yfinance_query"}
    )
    
    workflow.add_conditional_edges(
        "yfinance_query",
        lambda s: "generate" if s['documents'] else "ddg_query",
        {"generate": "generate", "ddg_query": "ddg_query"}
    )
    
    workflow.add_edge("ddg_query", "generate")
    workflow.add_edge("generate", "store_memory")
    workflow.add_edge("store_memory", END)
    
    return workflow.compile()