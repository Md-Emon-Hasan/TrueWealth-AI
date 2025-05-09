from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents import nodes

def create_workflow(retriever):
    workflow = StateGraph(AgentState)
    workflow.add_node("planner", nodes.planner)
    workflow.add_node("recall_memory", nodes.recall_memory)
    workflow.add_node("llm_query", nodes.query_llm)
    workflow.add_node("executor", nodes.executor)
    workflow.add_node("rag_query", lambda s: nodes.retrieve_docs(s, retriever))
    workflow.add_node("yfinance_query", nodes.retrieve_yfinance)
    workflow.add_node("ddg_query", nodes.retrieve_duckduckgo)
    workflow.add_node("generate", nodes.generate_response)
    workflow.add_node("store_memory", nodes.store_memory)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "recall_memory")
    workflow.add_edge("recall_memory", "llm_query")
    workflow.add_conditional_edges("llm_query", lambda s: "generate" if s.get("generation") else "executor", {"generate": "generate", "executor": "executor"})
    workflow.add_conditional_edges("executor", lambda s: "rag_query" if s['retry_count'] < 3 else "yfinance_query", {"rag_query": "rag_query", "yfinance_query": "yfinance_query"})
    workflow.add_conditional_edges("rag_query", lambda s: "generate" if s['documents'] else "yfinance_query", {"generate": "generate", "yfinance_query": "yfinance_query"})
    workflow.add_conditional_edges("yfinance_query", lambda s: "generate" if s['documents'] else "ddg_query", {"generate": "generate", "ddg_query": "ddg_query"})
    workflow.add_edge("ddg_query", "generate")
    workflow.add_edge("generate", "store_memory")
    workflow.add_edge("store_memory", END)

    return workflow.compile()