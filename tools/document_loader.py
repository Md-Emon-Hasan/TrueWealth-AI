from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.config import PDF_PATH, CHUNK_SIZE, CHUNK_OVERLAP

def load_documents():
    """Load and split PDF documents"""
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    return docs

def split_documents(docs):
    """Split documents into chunks"""
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", ". ", "\n", " "]
    )
    doc_splits = text_splitter.split_documents(docs)
    return doc_splits