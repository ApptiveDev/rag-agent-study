from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from abc import ABC, abstractmethod
from operator import itemgetter
from pathlib import Path
import hashlib


RAG_PROMPT_TEMPLATE = """당신은 스타듀밸리 게임 전문가입니다.
주어진 컨텍스트(위키 문서)를 바탕으로 질문에 답하세요.
컨텍스트에 없는 내용은 추측하지 말고, 모른다고 명확히 밝히세요.

컨텍스트:
{context}

질문: {question}

답변 (근거 문서 출처를 마지막에 반드시 표시):"""


class RetrievalChain(ABC):
    def __init__(self):
        self.source_uri = None
        self.k = 6
        self.model_name = "gpt-4o-mini"
        self.temperature = 0
        self.embeddings = "text-embedding-3-small"
        self.index_dir = Path(".cache/faiss_index")

    @abstractmethod
    def load_documents(self, source_uris):
        pass

    @abstractmethod
    def create_text_splitter(self):
        pass

    def split_documents(self, docs, text_splitter):
        return text_splitter.split_documents(docs)

    def create_embedding(self):
        return OpenAIEmbeddings(model=self.embeddings)

    def create_vectorstore(self, split_docs):
        try:
            self.index_dir.mkdir(parents=True, exist_ok=True)

            doc_contents = "\n".join([doc.page_content for doc in split_docs])
            doc_hash = hashlib.md5(doc_contents.encode()).hexdigest()

            hash_file = self.index_dir / "doc_hash.txt"
            index_path = str(self.index_dir / "faiss_index")

            try:
                if (
                    hash_file.exists()
                    and Path(index_path + ".faiss").exists()
                    and hash_file.read_text().strip() == doc_hash
                ):
                    vectorstore = FAISS.load_local(
                        index_path,
                        self.create_embedding(),
                        allow_dangerous_deserialization=True,
                    )
                    print("Loaded existing FAISS index from cache")
                    return vectorstore
            except Exception as e:
                print(f"Warning: Failed to load existing index: {e}")

            vectorstore = FAISS.from_documents(
                documents=split_docs, embedding=self.create_embedding()
            )

            try:
                vectorstore.save_local(index_path)
                hash_file.write_text(doc_hash)
                print("FAISS index saved to cache")
            except Exception as e:
                print(f"Warning: Failed to save index: {e}")

            return vectorstore

        except Exception as e:
            print(f"Error creating vectorstore with cache: {e}. Falling back.")
            return FAISS.from_documents(
                documents=split_docs, embedding=self.create_embedding()
            )

    def create_retriever(self, vectorstore):
        return vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": self.k}
        )

    def create_model(self):
        return init_chat_model(self.model_name, temperature=self.temperature)

    def create_prompt(self):
        return ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    def create_chain(self):
        docs = self.load_documents(self.source_uri)
        text_splitter = self.create_text_splitter()
        split_docs = self.split_documents(docs, text_splitter)
        self.vectorstore = self.create_vectorstore(split_docs)
        self.retriever = self.create_retriever(self.vectorstore)
        model = self.create_model()
        prompt = self.create_prompt()
        self.chain = (
            {"question": itemgetter("question"), "context": itemgetter("context")}
            | prompt
            | model
            | StrOutputParser()
        )
        return self
