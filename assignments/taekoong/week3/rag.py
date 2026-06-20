from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)
from langchain_openai import (
    OpenAIEmbeddings,
    ChatOpenAI,
)
from langchain_chroma import Chroma

loader = DirectoryLoader(
    "./data",
    glob="**/*.txt",
    loader_cls=TextLoader,
)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
chunks = splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
)

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,
        "fetch_k": 10,
    }
)
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

question = input("Question: ")

rewrite_prompt = f"""
Translate the following Minecraft question into English.

Question:
{question}

Return only the translated question.
"""

rewritten_question = llm.invoke(
    rewrite_prompt
).content.strip()

print("\nOriginal Question:")
print(question)

print("\nRewritten Question:")
print(rewritten_question)


retrieved_docs = retriever.invoke(
    rewritten_question
)

print("\nRetrieved Documents:\n")

for doc in retrieved_docs:
    print(doc.metadata["source"])

context = "\n\n".join(
    doc.page_content
    for doc in retrieved_docs
)

prompt = f"""
In Korean,
Answer the question using ONLY the provided context.

Context:
{context}

Question:
{question}
"""
response = llm.invoke(prompt)

print("\nAnswer:\n")
print(response.content)

print("\nSources:")
sources = set()
for doc in retrieved_docs:
    sources.add(
        doc.metadata["source"]
    )
for source in sources:
    print("-", source)