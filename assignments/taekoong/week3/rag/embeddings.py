from langchain_openai import OpenAIEmbeddings


def get_embeddings(model: str = "text-embedding-3-small"):
    return OpenAIEmbeddings(model=model)
