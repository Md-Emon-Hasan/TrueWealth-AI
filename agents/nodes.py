from langchain.schema import Document
from langchain_groq import ChatGroq
from logger import logger
from config import GROQ_API_KEY
from tools.external_tools import load_tools

llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.3, max_tokens=2048)
tools = load_tools()

def planner(state):
    logger.info("Running planner node.")
    state['retry_count'] = 0
    return state

def recall_memory(state):
    logger.info("Recalling memory.")
    state['conversation_history'] = state.get('memory', [])[-10:]
    return state

def query_llm(state):
    logger.info("Querying LLM with client question.")
    ctx = "\n".join(state['conversation_history'])
    prompt = f"""You are a trusted financial advisor.\n{ctx}\nClient: {state['question']}\nRespond professionally in 2–3 sentences."""
    res = llm.invoke(prompt).content.strip()
    state.update({
        "generation": res,
        "source": "llm_knowledge",
        "llm_attempted": True
    })
    state['conversation_history'] += [f"Client: {state['question']}", f"Advisor: {res}"]
    return state

def executor(state):
    logger.info("Executing fallback logic.")
    state['retry_count'] += 1
    return state

def retrieve_docs(state, retriever):
    logger.info("Retrieving from ChromaDB.")
    ctx = "\n".join(state['conversation_history'])
    query = f"Context: {ctx}\nQuestion: {state['question']}" if ctx else state['question']
    docs = retriever.invoke(query)
    state.update({
        'documents': docs,
        'rag_attempted': True,
        'search_query': query,
        'source': 'rag_documents'
    })
    state['conversation_history'] += ["AI: Searching financial documents..."]
    return state

def retrieve_yfinance(state):
    logger.info("Retrieving Yahoo Finance news.")
    content = tools['yfinance'].invoke(state['question'])
    state.update({
        'documents': [Document(page_content=content)],
        'yfinance_attempted': True,
        'source': 'yfinance'
    })
    state['conversation_history'] += ["AI: Searching Yahoo Finance..."]
    return state

def retrieve_duckduckgo(state):
    logger.info("Searching DuckDuckGo.")
    content = tools['duckduckgo'].invoke(state['question'])
    state.update({
        'documents': [Document(page_content=content)],
        'ddg_attempted': True,
        'source': 'duckduckgo'
    })
    state['conversation_history'] += ["AI: Searching DuckDuckGo..."]
    return state

def generate_response(state):
    logger.info(f"Generating final response from source: {state['source']}")
    if state['source'] == 'llm_knowledge':
        return state

    if state['documents']:
        content = "\n".join(doc.page_content for doc in state['documents'])
        ctx = "\n".join(state['conversation_history'][-3:])
        prompt = f"""Client: {state['question']}\n{ctx}\nRelevant Info:\n{content}\nRespond professionally in 2–3 sentences."""
        res = llm.invoke(prompt).content.strip()
        state['generation'] = res
        state['conversation_history'] += [f"Advisor: {res}"]
        return state

    state['generation'] = "I'm unable to answer confidently. Please consult a financial expert."
    state['conversation_history'] += [state['generation']]
    return state

def store_memory(state):
    logger.info("Storing memory.")
    state['memory'] = state['conversation_history']
    return state