import streamlit as st
import os
import os.path
from typing import TypedDict, List, Optional
from dotenv import load_dotenv

# PDF loading, text splitting, and vector store handling
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Embeddings from HuggingFace
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# LLM model from Groq
from langchain_groq import ChatGroq

# Search and tool integrations
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

# LangGraph for graph-based agent logic
from langgraph.graph import StateGraph, END
from langchain.schema import Document

# Set page configuration
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Define the path to the book
base_dir = os.path.dirname(os.path.abspath(__file__))
BOOK_PATH = os.path.join(base_dir, "data", "The Intelligent Investor - BENJAMIN GRAHAM.pdf")

# Memory-tracking and reasoning state format
class AgentState(TypedDict):
    question: str
    documents: List[Document]
    generation: str
    source: str
    search_query: Optional[str]
    conversation_history: List[str]
    llm_attempted: bool
    rag_attempted: bool
    yfinance_attempted: bool
    ddg_attempted: bool
    retry_count: int
    memory: List[str]

# Initialize session states
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.conversation_state = {
        "question": "",
        "documents": [],
        "generation": "",
        "source": "",
        "search_query": None,
        "conversation_history": [],
        "llm_attempted": False,
        "rag_attempted": False,
        "yfinance_attempted": False,
        "ddg_attempted": False,
        "retry_count": 0,
        "memory": []
    }
    st.session_state.chat_history = []
    st.session_state.workflow_ready = False

# Check if the book exists
if not os.path.exists(BOOK_PATH):
    st.error(f"The book file doesn't exist at '{BOOK_PATH}'. Please make sure the file is in the correct location.")

# Sidebar for API key input
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # API Key Input
    api_key = st.text_input("Enter Groq API Key:", type="password")
    if api_key:
        os.environ['GROQ_API_KEY'] = api_key
    
    st.divider()
    
    # Book information
    st.subheader("Knowledge Source")
    st.info(f"Using: The Intelligent Investor by Benjamin Graham")

# Main app functions
def setup_workflow():
    """Set up the entire workflow with the financial book"""
    if not os.environ.get('GROQ_API_KEY'):
        st.error("Please enter your Groq API Key in the sidebar.")
        return False
    
    if not os.path.exists(BOOK_PATH):
        st.error(f"The book file doesn't exist at '{BOOK_PATH}'. Please make sure the file is in the correct location.")
        return False
    
    with st.spinner("Setting up AI advisor workflow..."):
        try:
            # Load PDF
            loader = PyPDFLoader(BOOK_PATH)
            docs = loader.load()
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=512,
                chunk_overlap=128,
                separators=["\n\n", ". ", "\n", " "]
            )
            doc_splits = text_splitter.split_documents(docs)
            
            # Set up embeddings and vector store
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            
            # Store vectors in ChromaDB
            vectorstore = Chroma.from_documents(
                documents=doc_splits,
                embedding=embeddings,
                persist_directory="./financial_db",
                collection_metadata={"hnsw:space": "cosine"}
            )
            
            # Create retriever
            retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
            
            # Set up LLM
            llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.3, max_tokens=2048)
            
            # Set up tools
            yahoo_finance_news = YahooFinanceNewsTool()
            duckduckgo_search = DuckDuckGoSearchRun()
            
            # --- Node Functions ---
            
            # Start of graph; resets retry counter
            def planner(state: AgentState):
                state['retry_count'] = 0
                return state

            # Loads last 10 interactions from memory
            def recall_memory(state: AgentState):
                state['conversation_history'] = state.get('memory', [])[-10:]
                return state

            # Initial attempt: direct LLM answer
            def query_llm(state: AgentState):
                ctx = "\n".join(state['conversation_history'])
                prompt = f"""You are a trusted, knowledgeable, and insightful AI-powered financial advisor.

Client's Financial History & Discussion:
{ctx}

Client's Query:
{state['question']}

Respond like an experienced financial advisor in 2–3 sentences. Be professional, concise, and confident. Avoid mentioning data sources or expressing uncertainty."""
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

            # Retry routing logic node
            def executor(state: AgentState):
                state['retry_count'] += 1
                return state

            # RAG document retrieval (from ChromaDB)
            def retrieve_docs(state: AgentState):
                ctx = "\n".join(state['conversation_history'])
                query = f"Context: {ctx}\nQuestion: {state['question']}" if ctx else state['question']
                docs = retriever.invoke(query)
                state['documents'] = docs
                state['rag_attempted'] = True
                state['search_query'] = query
                state['conversation_history'] += ["AI: Searching financial documents..."]
                state['source'] = 'rag_documents'
                return state

            # Yahoo Finance News Tool fallback
            def retrieve_yfinance(state: AgentState):
                content = yahoo_finance_news.invoke(state['question'])
                state['documents'] = [Document(page_content=content)]
                state['yfinance_attempted'] = True
                state['source'] = 'yfinance'
                state['conversation_history'] += ["AI: Searching yfinance..."]
                return state

            # DuckDuckGo Search Fallback
            def retrieve_duckduckgo(state: AgentState):
                content = duckduckgo_search.invoke(state['question'])
                state['documents'] = [Document(page_content=content)]
                state['ddg_attempted'] = True
                state['source'] = 'duckduckgo'
                state['conversation_history'] += ["AI: Searching DuckDuckGo..."]
                return state

            # Final response generation based on tool context
            def generate_response(state: AgentState):
                if state['source'] == 'llm_knowledge':
                    return state

                if state['documents']:
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

            # Store new memory for future sessions
            def store_memory(state: AgentState):
                state['memory'] = state['conversation_history']
                return state

            # --- Build Graph Workflow ---
            workflow = StateGraph(AgentState)
            workflow.add_node("planner", planner)
            workflow.add_node("recall_memory", recall_memory)
            workflow.add_node("llm_query", query_llm)
            workflow.add_node("executor", executor)
            workflow.add_node("rag_query", retrieve_docs)
            workflow.add_node("yfinance_query", retrieve_yfinance)
            workflow.add_node("ddg_query", retrieve_duckduckgo)
            workflow.add_node("generate", generate_response)
            workflow.add_node("store_memory", store_memory)

            # Entry point
            workflow.set_entry_point("planner")

            # Define edge conditions for branching
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

            # Compile graph app
            app = workflow.compile()
            
            # Store in session state
            st.session_state.app = app
            st.session_state.workflow_ready = True
            
            return True
            
        except Exception as e:
            st.error(f"Error setting up workflow: {str(e)}")
            return False

# Main application layout
st.title("TrueWealth AI: Your Smart Path to Financial Freedom")
st.markdown("""
This application helps you get financial advice by analyzing 'The Intelligent Investor' by Benjamin Graham
and leveraging additional information from Yahoo Finance and web searches when needed.
""")
st.markdown("Presented by: **Md Emon Hasan**")
  
# Add CSS for chat styling
st.markdown("""
<style>
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
}
.user-message {
    background-color: #E9F5FE;
    padding: 10px 15px;
    border-radius: 20px 20px 0 20px;
    margin-left: auto;
    margin-right: 10px;
    max-width: 80%;
    align-self: flex-end;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.assistant-message {
    background-color: #F0F2F6;
    padding: 10px 15px;
    border-radius: 20px 20px 20px 0;
    margin-right: auto;
    margin-left: 10px;
    max-width: 80%;
    align-self: flex-start;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.message-container {
    display: flex;
    margin-bottom: 10px;
}
.message-avatar {
    width: 35px;
    height: 35px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
    margin-right: 10px;
}
.user-avatar {
    background-color: #4F8BF9;
}
.assistant-avatar {
    background-color: #36B37E;
}
.message-content {
    margin-left: 10px;
}
.message-time {
    font-size: 0.7em;
    color: gray;
    text-align: right;
    margin-top: 5px;
}
.input-container {
    display: flex;
    gap: 10px;
}
.input-field {
    flex-grow: 1;
}
</style>
""", unsafe_allow_html=True)

# Setup button
if not st.session_state.workflow_ready:
    if st.button("Initialize Financial Advisor"):
        if setup_workflow():
            st.success("Financial advisor is ready to answer your questions!")
            st.session_state.initialized = True
            st.rerun()

# Chat interface
if st.session_state.workflow_ready:
    # Create a container for the chat
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f'''
                <div class="message-container" style="justify-content: flex-end;">
                    <div class="user-message">{chat['content']}</div>
                    <div class="message-avatar user-avatar">U</div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="message-container">
                    <div class="message-avatar assistant-avatar">AI</div>
                    <div class="assistant-message">{chat['content']}</div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    
    # Create a key that changes when we want to reset the input
    if "reset_counter" not in st.session_state:
        st.session_state.reset_counter = 0
    
    input_key = f"user_query_{st.session_state.reset_counter}"
    
    with col1:
        user_query = st.text_input("", placeholder="Ask a financial question...", key=input_key, label_visibility="collapsed")
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if send_button and user_query:
        # Add user query to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # Update conversation state
        st.session_state.conversation_state.update({
            "question": user_query,
            "generation": "",
            "documents": [],
            "source": "",
            "retry_count": 0
        })
        
        # Process with the workflow
        with st.spinner("Thinking..."):
            result = st.session_state.app.invoke(st.session_state.conversation_state)
            st.session_state.conversation_state.update(result)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": st.session_state.conversation_state['generation']
        })
        
        # Increment the counter to reset the input field
        st.session_state.reset_counter += 1
        
        # Rerun to update the display
        st.rerun()

# Debug information (can be commented out in production)
with st.sidebar.expander("Debug Info", expanded=False):
    st.write("Workflow Ready:", st.session_state.workflow_ready)
    st.write("Book Path:", BOOK_PATH)
    st.write("Book Exists:", os.path.exists(BOOK_PATH))
    if st.session_state.workflow_ready:
        st.write("Last Source:", st.session_state.conversation_state['source'])
        st.write("RAG Attempted:", st.session_state.conversation_state['rag_attempted'])
        st.write("YFinance Attempted:", st.session_state.conversation_state['yfinance_attempted'])
        st.write("DDG Attempted:", st.session_state.conversation_state['ddg_attempted'])

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("AI Financial Advisor powered by Groq & LangGraph")