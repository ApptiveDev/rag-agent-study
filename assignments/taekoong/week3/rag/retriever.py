def get_retriever(vectorstore, k: int = 3, fetch_k: int = 10):
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k},
    )
