from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

def build_vectorstore(docs, persist_dir="./finance_db"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_metadata={"hnsw:space": "cosine"}
    )