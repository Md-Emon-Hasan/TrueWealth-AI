import os
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from core.config import EMBEDDINGS_MODEL, VECTOR_DB_PATH, RETRIEVAL_K
from tools.document_loader import load_documents, split_documents

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)

def setup_vector_store():
    embeddings = get_embeddings()
    
    # Ensure absolute path
    abs_vector_path = os.path.abspath(VECTOR_DB_PATH)
    print(f"Vector DB path: {abs_vector_path}")
    
    # Check if vector store already exists
    if os.path.exists(abs_vector_path) and os.listdir(abs_vector_path):
        print(f"Vector store found at: {abs_vector_path}")
        try:
            vectorstore = Chroma(
                persist_directory=abs_vector_path,
                embedding_function=embeddings,
                collection_name="finance_docs"
            )
        except Exception as e:
            print(f"Error loading existing vector store: {e}")
            print("Creating new vector store...")
            vectorstore = create_new_vectorstore(embeddings, abs_vector_path)
    else:
        print(f"Creating new vector store at: {abs_vector_path}")
        vectorstore = create_new_vectorstore(embeddings, abs_vector_path)
    
    return vectorstore

def create_new_vectorstore(embeddings, abs_vector_path):
    os.makedirs(abs_vector_path, exist_ok=True)
    
    # Check if PDF exists
    abs_pdf_path = os.path.abspath(PDF_PATH)
    print(f"Looking for PDF at: {abs_pdf_path}")
    
    if not os.path.exists(abs_pdf_path):
        print(f"WARNING: PDF not found at {abs_pdf_path}")

        vectorstore = Chroma(
            persist_directory=abs_vector_path,
            embedding_function=embeddings,
            collection_name="finance_docs"
        )
        return vectorstore
    
    # Load and split documents
    docs = load_documents()
    doc_splits = split_documents(docs)
    print(f"Loaded {len(doc_splits)} document chunks")
    
    # Create new vector store
    print("Creating embeddings and storing in vector database...")
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        embedding=embeddings,
        persist_directory=abs_vector_path,
        collection_name="finance_docs"
    )
    
    print(f"Vector store created and persisted at: {abs_vector_path}")
    print(f"Directory contents: {os.listdir(abs_vector_path) if os.path.exists(abs_vector_path) else 'Directory not found'}")
    
    return vectorstore

def get_retriever():
    """Get retriever from vector store"""
    vectorstore = setup_vector_store()
    return vectorstore.as_retriever(search_kwargs={'k': RETRIEVAL_K})