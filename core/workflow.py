# core/workflow.py
from langgraph.graph import StateGraph, END
from agents import (
    PlannerAgent, MemoryRecallAgent, LLMAgent,
    ExecutorAgent, RagAgent, YFinanceAgent,
    DuckDuckGoAgent, ResponseGenerator, MemoryStoreAgent
)
from core.state import AgentState

def get_workflow_app():
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("planner", PlannerAgent.process)
    workflow.add_node("recall_memory", MemoryRecallAgent.process)
    workflow.add_node("llm_query", LLMAgent.process)
    workflow.add_node("executor", ExecutorAgent.process)
    workflow.add_node("rag_query", RagAgent.process)
    workflow.add_node("yfinance_query", YFinanceAgent.process)
    workflow.add_node("ddg_query", DuckDuckGoAgent.process)
    workflow.add_node("generate", ResponseGenerator.process)
    workflow.add_node("store_memory", MemoryStoreAgent.process)

    # Set edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "recall_memory")
    workflow.add_edge("recall_memory", "llm_query")

    workflow.add_conditional_edges(
        "llm_query",
        lambda s: "generate" if s.get('generation') else "executor",
        {"generate": "generate", "executor": "executor"}
    )

    workflow.add_conditional_edges(
        "executor",
        lambda s: "rag_query" if s['retry_count'] < 3 else "yfinance_query",
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