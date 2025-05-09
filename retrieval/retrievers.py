def get_retriever(vectorstore, k=3):
    return vectorstore.as_retriever(search_kwargs={"k": k})