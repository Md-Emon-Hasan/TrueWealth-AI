import os

from app.core.config import DB_DIR, EMBEDDINGS_MODEL, PDF_PATH
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)


def create_new_vectorstore(embeddings, persist_directory):
    from app.tools.document_loader import load_documents, split_documents
    if not os.path.exists(PDF_PATH):
        return Chroma(embedding_function=embeddings, persist_directory=persist_directory)

    docs = load_documents(PDF_PATH)
    splits = split_documents(docs)

    os.makedirs(persist_directory, exist_ok=True)
    return Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=persist_directory
    )


def setup_vector_store():
    embeddings = get_embeddings()
    persist_directory = DB_DIR

    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        try:
            return Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
              )
        except Exception:
            return create_new_vectorstore(embeddings, persist_directory)
    else:
        return create_new_vectorstore(embeddings, persist_directory)


def get_retriever():
    vectorstore = setup_vector_store()
    return vectorstore.as_retriever(search_kwargs={"k": 3})
