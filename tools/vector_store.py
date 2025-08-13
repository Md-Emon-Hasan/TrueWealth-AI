# tools/vector_store.py
from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from .document_loader import load_pdf_documents
from core.config import VECTOR_DB_DIR

_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
_vectorstore = None

def initialize_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        docs = load_pdf_documents()
        _vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=_embeddings,
            persist_directory=str(VECTOR_DB_DIR),
            collection_metadata={"hnsw:space": "cosine"}
        )
    return _vectorstore

def get_retriever():
    if _vectorstore is None:
        initialize_vectorstore()
    return _vectorstore.as_retriever(search_kwargs={'k': 3})