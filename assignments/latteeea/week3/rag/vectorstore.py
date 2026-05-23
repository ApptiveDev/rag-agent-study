from pathlib import Path
import shutil

from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv()

def get_embedding_model() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model="text-embedding-3-small")

def build_faiss_vectorstore(chunks: list[Document]) -> FAISS:
    """
    chunks 리스트를 embedding해서 FAISS vector store를 생성한다. 
    """
    embeddings = get_embedding_model()
    
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )
    
    return vectorstore

def save_faiss_vectorstore(vectorstore: FAISS, index_dir: str) -> None:
    """
    FAISS index를 로컬 디렉토리에 저장한다. 
    """
    path = Path(index_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    vectorstore.save_local(str(path))
    
def load_faiss_vectorstore(index_dir: str) -> None:
    """
    저장된 FAISS index 로드하기 
    """
    embeddings = get_embedding_model()
    
    return FAISS.load_local(
        folder_path=index_dir,
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )
    
def reset_faiss_index(index_dir: str) -> None:
    """
    기존 FAISS index 디렉토리 삭제 
    """
    path = Path(index_dir)
    
    if path.exists():
        shutil.rmtree(path)