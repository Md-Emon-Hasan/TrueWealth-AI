# tools/document_loader.py
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.config import DATA_DIR

def load_pdf_documents(filename="Rasel_Sarker_Resume (1).pdf"):
    loader = PyPDFLoader(str(DATA_DIR / filename))
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512,
        chunk_overlap=128,
        separators=["\n\n", ". ", "\n", " "]
    )
    
    return splitter.split_documents(docs)