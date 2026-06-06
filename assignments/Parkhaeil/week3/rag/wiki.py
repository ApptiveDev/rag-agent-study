from rag.base import RetrievalChain
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from typing import List, Literal, Annotated
from pathlib import Path
import os


CATEGORY_MAP = {
    "farming": "농사",
    "fishing": "낚시",
    "mining": "광산",
    "foraging": "채집",
    "livestock": "축산",
    "villagers": "주민",
    "crafting": "제작",
    "combat": "전투",
    "misc": "기타",
}

# MarkdownHeaderTextSplitter에서 추적할 헤더 레벨
MARKDOWN_HEADERS = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]


class WikiRetrievalChain(RetrievalChain):
    """스타듀밸리 위키 마크다운 파일 기반 RAG 체인.

    Args:
        source_uri: 마크다운 파일이 담긴 디렉토리 경로 (또는 파일 경로 리스트)
        splitter_type: "recursive" | "markdown_header"
        chunk_size: RecursiveCharacterTextSplitter 청크 크기 (recursive 전용)
        chunk_overlap: 오버랩 크기 (recursive 전용)
    """

    def __init__(
        self,
        source_uri: Annotated[str | list, "마크다운 디렉토리 경로 또는 파일 경로 리스트"],
        splitter_type: Literal["recursive", "markdown_header"] = "recursive",
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.source_uri = source_uri
        self.splitter_type = splitter_type
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 캐시 디렉토리를 splitter 타입별로 분리 (비교 실험용)
        cache_suffix = f"stardew_wiki_{splitter_type}"
        self.index_dir = Path(f".cache/faiss_index/{cache_suffix}")

    def _infer_category(self, file_path: str) -> str:
        """파일명/경로에서 카테고리 추론."""
        name = Path(file_path).stem.lower()
        for key, label in CATEGORY_MAP.items():
            if key in name:
                return label
        return "기타"

    def load_documents(self, source_uris) -> List[Document]:
        """마크다운 파일들을 로드하고 category 메타데이터 부착."""
        if isinstance(source_uris, str):
            path = Path(source_uris)
            if path.is_dir():
                file_paths = sorted(path.glob("**/*.md"))
            else:
                file_paths = [path]
        else:
            file_paths = [Path(p) for p in source_uris]

        docs = []
        failed = []
        for fp in file_paths:
            try:
                if not fp.exists():
                    print(f"Warning: Not found: {fp}")
                    failed.append(str(fp))
                    continue
                text = fp.read_text(encoding="utf-8")
                if not text.strip():
                    continue
                category = self._infer_category(str(fp))
                doc = Document(
                    page_content=text,
                    metadata={
                        "source": str(fp),
                        "category": category,
                        "filename": fp.name,
                    },
                )
                docs.append(doc)
                print(f"Loaded: {fp.name} ({category})")
            except Exception as e:
                print(f"Error loading {fp}: {e}")
                failed.append(str(fp))

        print(f"\nLoaded {len(docs)} documents, {len(failed)} failed.")
        if not docs:
            raise ValueError("No documents loaded.")
        return docs

    def create_text_splitter(self):
        if self.splitter_type == "markdown_header":
            return MarkdownHeaderTextSplitter(
                headers_to_split_on=MARKDOWN_HEADERS,
                strip_headers=False,
            )
        else:
            return RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
            )

    def split_documents(self, docs, text_splitter):
        """splitter 타입에 따라 분할 로직을 다르게 처리."""
        if self.splitter_type == "markdown_header":
            split_docs = []
            for doc in docs:
                splits = text_splitter.split_text(doc.page_content)
                for split in splits:
                    # MarkdownHeaderTextSplitter는 Document를 반환하므로
                    # 원본 doc의 메타데이터를 병합
                    merged_meta = {**doc.metadata, **split.metadata}
                    split_docs.append(
                        Document(
                            page_content=split.page_content,
                            metadata=merged_meta,
                        )
                    )
            print(f"Split into {len(split_docs)} chunks (markdown_header)")
            return split_docs
        else:
            split_docs = text_splitter.split_documents(docs)
            print(f"Split into {len(split_docs)} chunks (recursive, size={self.chunk_size})")
            return split_docs
