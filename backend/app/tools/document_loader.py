from app.core.config import CHUNK_OVERLAP, CHUNK_SIZE
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_documents(pdf_path=""):
    if not pdf_path:
        from app.core.config import PDF_PATH
        pdf_path = PDF_PATH
    loader = PyPDFLoader(pdf_path)
    return loader.load()


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return text_splitter.split_documents(documents)
