from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512,
        chunk_overlap=128,
        separators=["\n\n", ". ", "\n", " "]
    )
    return splitter.split_documents(docs)