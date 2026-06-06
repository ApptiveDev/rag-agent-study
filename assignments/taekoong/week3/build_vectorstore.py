from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

## loader 
loader = DirectoryLoader(
    "./data",
    glob="**/*.txt",
    loader_cls=TextLoader,
)

docs = loader.load()

## splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

chunks = splitter.split_documents(docs)

print("청크 수:", len(chunks))

## embedding
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

## chroma
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

## test csearch
results = vectorstore.similarity_search(
    "What is the use of a diamond?",
    k=3
)

for i, doc in enumerate(results):
    print(f"\n=== Result {i+1} ===")
    print(doc.metadata["source"])
    print(doc.page_content[:300])