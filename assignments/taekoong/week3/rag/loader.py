from langchain_community.document_loaders import DirectoryLoader, TextLoader


def load_docs(path: str = "./data"):
    loader = DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader)
    return loader.load()
