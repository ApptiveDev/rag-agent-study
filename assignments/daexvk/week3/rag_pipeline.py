import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.feature_extraction.text import TfidfVectorizer

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
DEFAULT_HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_project_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    os.environ.setdefault("LANGSMITH_TRACING", "false")
    os.environ.setdefault("LANGSMITH_TRACING_V2", "false")


@dataclass
class RagIndex:
    strategy: str
    documents: list[Document]
    chunks: list[Document]
    embeddings: Embeddings
    vectorstore: FAISS


class SentenceTransformerEmbeddings(Embeddings):
    """HuggingFace sentence-transformers embedding wrapper.

    Used when sentence_transformers is installed and the model is available.
    """

    def __init__(self, model_name: str = DEFAULT_HF_MODEL):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([text], normalize_embeddings=True, show_progress_bar=False)[0].tolist()


class TfidfEmbeddings(Embeddings):
    """Local free fallback embedding model with the same index/query interface."""

    def __init__(self):
        self.model_name = "local:sklearn-tfidf"
        self.vectorizer = TfidfVectorizer(max_features=8192, ngram_range=(1, 2), lowercase=True)
        self._is_fit = False

    def fit(self, texts: list[str]) -> "TfidfEmbeddings":
        self.vectorizer.fit(texts)
        self._is_fit = True
        return self

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not self._is_fit:
            self.fit(texts)
        return self.vectorizer.transform(texts).toarray().astype("float32").tolist()

    def embed_query(self, text: str) -> list[float]:
        if not self._is_fit:
            raise RuntimeError("TfidfEmbeddings must be fit on documents before querying.")
        return self.vectorizer.transform([text]).toarray().astype("float32")[0].tolist()


def create_embedding_model(texts: list[str], prefer_huggingface: bool = True) -> Embeddings:
    """Use the free HuggingFace model if available; otherwise use local TF-IDF.

    Both indexing and querying use the exact same returned object.
    """

    if prefer_huggingface:
        try:
            return SentenceTransformerEmbeddings(os.getenv("RAG_EMBEDDING_MODEL", DEFAULT_HF_MODEL))
        except Exception as exc:
            print(f"HuggingFace embedding unavailable, using TF-IDF fallback: {type(exc).__name__}: {exc}")

    return TfidfEmbeddings().fit(texts)


def load_raw_documents(data_dir: Path = DATA_DIR) -> list[Document]:
    documents = []
    for path in sorted(data_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        title = path.stem[3:].replace("_", " ").title()
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source_file": path.name,
                    "source_path": str(path),
                    "title": title,
                },
            )
        )
    return documents


def split_recursive(documents: list[Document], chunk_size: int = 1200, chunk_overlap: int = 180) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = [chunk for chunk in splitter.split_documents(documents) if len(chunk.page_content.strip()) >= 180]
    return _add_chunk_metadata(chunks, "recursive_character")


def split_token(documents: list[Document], chunk_tokens: int = 220, token_overlap: int = 45) -> list[Document]:
    """Token-like splitter using whitespace tokens to avoid external tokenizer downloads."""

    chunks: list[Document] = []
    step = max(1, chunk_tokens - token_overlap)
    for doc in documents:
        tokens = doc.page_content.split()
        for start in range(0, len(tokens), step):
            window = tokens[start : start + chunk_tokens]
            if not window:
                continue
            content = " ".join(window)
            if len(content.strip()) < 180:
                continue
            metadata = dict(doc.metadata)
            metadata.update({"token_start": start, "token_end": start + len(window)})
            chunks.append(Document(page_content=content, metadata=metadata))
            if start + chunk_tokens >= len(tokens):
                break
    return _add_chunk_metadata(chunks, "token")


def _add_chunk_metadata(chunks: list[Document], strategy: str) -> list[Document]:
    for index, chunk in enumerate(chunks):
        chunk.metadata = dict(chunk.metadata)
        chunk.metadata["strategy"] = strategy
        chunk.metadata["chunk_index"] = index
        chunk.metadata["source_id"] = f"{chunk.metadata.get('source_file')}#{index}"
    return chunks


def build_index(
    strategy: Literal["recursive", "token"],
    documents: list[Document] | None = None,
    prefer_huggingface: bool = True,
) -> RagIndex:
    if documents is None:
        documents = load_raw_documents()

    if strategy == "recursive":
        chunks = split_recursive(documents)
    elif strategy == "token":
        chunks = split_token(documents)
    else:
        raise ValueError(f"unsupported strategy: {strategy}")

    texts = [chunk.page_content for chunk in chunks]
    embeddings = create_embedding_model(texts, prefer_huggingface=prefer_huggingface)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return RagIndex(strategy=strategy, documents=documents, chunks=chunks, embeddings=embeddings, vectorstore=vectorstore)


QUERY_EXPANSIONS = {
    "베토벤 5번": "Symphony No. 5 Beethoven Fate Symphony four note motif movements",
    "베토벤 교향곡 5번": "Symphony No. 5 Beethoven Fate Symphony four note motif movements",
    "베토벤 9번": "Symphony No. 9 Beethoven Ode to Joy choral symphony",
    "베토벤 교향곡 9번": "Symphony No. 9 Beethoven Ode to Joy choral symphony",
    "말러 5번": "Symphony No. 5 Mahler Adagietto trumpet funeral march movements",
    "말러 교향곡 5번": "Symphony No. 5 Mahler Adagietto trumpet funeral march movements",
    "드보르자크 9번": "Symphony No. 9 Dvorak New World Symphony Largo",
    "드보르자크 교향곡 9번": "Symphony No. 9 Dvorak New World Symphony Largo",
    "클래식": "classical music",
    "공연예절": "concert etiquette applause attire mobile phone",
    "공연 예절": "concert etiquette applause attire mobile phone",
    "박수": "applause clap concert etiquette movement pause",
    "복장": "attire dress concert etiquette",
    "교향곡": "symphony orchestral work movement",
    "협주곡": "concerto soloist orchestra",
    "실내악": "chamber music string quartet ensemble",
    "소나타": "sonata",
    "악장": "movement",
    "동기": "motif theme",
    "첫 동기": "opening motif four note motif",
    "베토벤": "Beethoven Ludwig van Beethoven",
    "모차르트": "Mozart Wolfgang Amadeus Mozart",
    "바흐": "Bach Johann Sebastian Bach",
    "말러": "Mahler Gustav Mahler",
    "드뷔시": "Debussy Claude Debussy",
    "차이콥스키": "Tchaikovsky Pyotr Ilyich Tchaikovsky",
    "라흐마니노프": "Rachmaninoff Piano Concerto No. 2",
    "멘델스존": "Mendelssohn Violin Concerto",
    "엘가": "Elgar Cello Concerto",
    "비발디": "Vivaldi Four Seasons",
    "헨델": "Handel Messiah",
    "오르프": "Orff Carmina Burana",
    "볼레로": "Bolero Ravel",
    "봄의 제전": "The Rite of Spring Stravinsky",
    "사계": "The Four Seasons Vivaldi",
    "레퀴엠": "Requiem Mozart",
    "5번": "No. 5 fifth",
    "9번": "No. 9 ninth",
}


def expand_query(query: str) -> str:
    additions = []
    lowered = query.lower()
    for korean, english in QUERY_EXPANSIONS.items():
        if korean.lower() in lowered:
            additions.append(english)
    if not additions:
        return query
    return query + " " + " ".join(dict.fromkeys(additions))

TARGET_SOURCE_HINTS = {
    "베토벤 5": ["symphony_no_5_beethoven"],
    "베토벤 교향곡 5": ["symphony_no_5_beethoven"],
    "베토벤 9": ["symphony_no_9_beethoven"],
    "말러 5": ["symphony_no_5_mahler"],
    "말러 교향곡 5": ["symphony_no_5_mahler"],
    "드보르자크 9": ["symphony_no_9_dvorak"],
    "라흐마니노프": ["piano_concerto_no_2_rachmaninoff"],
    "멘델스존": ["violin_concerto_mendelssohn"],
    "엘가": ["cello_concerto_elgar"],
    "박수": ["concert_etiquette"],
    "공연 예절": ["concert_etiquette"],
    "교향곡": ["symphony"],
    "협주곡": ["concerto"],
    "실내악": ["chamber_music"],
}


def _target_source_hints(query: str) -> list[str]:
    lowered = query.lower()
    hints = []
    for key, values in TARGET_SOURCE_HINTS.items():
        if key.lower() in lowered:
            hints.extend(values)
    return list(dict.fromkeys(hints))


def _is_low_value_reference_chunk(doc: Document) -> bool:
    text = doc.page_content.strip().lower()
    low_value_prefixes = (
        "== references", "== notes", "== citations", "== sources", "== further reading",
        "== bibliography", "== external links", "=== notes", "=== citations", "=== sources",
    )
    bibliography_markers = (" doi:", " isbn", " pp.", " vol.", "journal", "quarterly", "bibliography")
    if text.startswith(low_value_prefixes):
        return True
    marker_hits = sum(1 for marker in bibliography_markers if marker in text)
    return marker_hits >= 2



def retrieve(index: RagIndex, query: str, k: int = 4) -> list[Document]:
    expanded_query = expand_query(query)
    fetch_k = max(24, k * 8)
    candidates = index.vectorstore.similarity_search_with_score(expanded_query, k=fetch_k)
    hints = _target_source_hints(query)

    reranked = []
    for rank, (doc, score) in enumerate(candidates):
        source_file = doc.metadata.get("source_file", "").lower()
        adjusted = float(score) + rank * 0.001
        if _is_low_value_reference_chunk(doc):
            adjusted += 1.5
        for hint in hints:
            if hint in source_file:
                adjusted -= 0.8
        reranked.append((adjusted, doc))

    reranked.sort(key=lambda item: item[0])
    return [doc for _, doc in reranked[:k]]


def compare_retrievers(indexes: dict[str, RagIndex], queries: Iterable[str], k: int = 4) -> list[dict]:
    rows = []
    for query in queries:
        for name, index in indexes.items():
            docs = retrieve(index, query, k=k)
            rows.append(
                {
                    "query": query,
                    "strategy": name,
                    "top_sources": [doc.metadata.get("source_id") for doc in docs],
                    "top_titles": [doc.metadata.get("title") for doc in docs],
                    "chunk_lengths": [len(doc.page_content) for doc in docs],
                }
            )
    return rows


def format_sources(docs: list[Document]) -> str:
    lines = []
    for i, doc in enumerate(docs, start=1):
        lines.append(
            f"[{i}] {doc.metadata.get('source_file')} "
            f"chunk={doc.metadata.get('chunk_index')} strategy={doc.metadata.get('strategy')}"
        )
    return "\n".join(lines)


def format_context(docs: list[Document], max_chars_per_doc: int = 1200) -> str:
    blocks = []
    for i, doc in enumerate(docs, start=1):
        snippet = doc.page_content[:max_chars_per_doc].replace("\n", " ")
        blocks.append(f"[source {i}: {doc.metadata.get('source_id')}]\n{snippet}")
    return "\n\n".join(blocks)


def generate_answer(question: str, docs: list[Document], use_llm: bool = True) -> str:
    """2-step RAG generate step. Falls back to extractive output if LLM is unavailable."""

    context = format_context(docs)
    sources = format_sources(docs)
    if use_llm:
        try:
            load_project_env()
            model_name = os.getenv("CLASSICAL_AGENT_MODEL", "openai:gpt-5.4-mini")
            model = init_chat_model(model_name)
            prompt = f"""
You are a Korean classical-concert prep assistant.
Answer the question using only the retrieved context.
If the context is insufficient, say what is uncertain.
Include a short Korean answer and then cite the source file list.

Question:
{question}

Retrieved context:
{context}

Source files:
{sources}
""".strip()
            response = model.invoke(prompt)
            return str(response.content)
        except Exception as exc:
            print(f"LLM generation unavailable, using extractive fallback: {type(exc).__name__}: {exc}")

    snippets = []
    useful_docs = [doc for doc in docs if not _is_low_value_reference_chunk(doc)] or docs
    for doc in useful_docs[:3]:
        text = doc.page_content.replace("\n", " ")[:550]
        snippets.append(f"- {text}")
    return (
        f"질문: {question}\n\n"
        "검색된 원문 근거에서 바로 확인되는 내용은 아래와 같습니다.\n"
        + "\n".join(snippets)
        + "\n\n근거 문서:\n"
        + sources
    )


def rag_answer(index: RagIndex, question: str, k: int = 4, use_llm: bool = True) -> dict:
    docs = retrieve(index, question, k=k)
    answer = generate_answer(question, docs, use_llm=use_llm)
    return {"question": question, "answer": answer, "documents": docs, "sources": format_sources(docs)}
