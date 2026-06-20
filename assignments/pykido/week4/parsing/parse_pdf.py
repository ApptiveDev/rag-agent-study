import os
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(), override=True)

WEEK4_DIR = Path(__file__).resolve().parent.parent
PARSED_DIR = WEEK4_DIR / "data" / "parsed"


def parse_pdf(pdf_path: str, output_stem: str | None = None) -> Path:
    from llama_parse import LlamaParse

    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    if not api_key:
        raise RuntimeError("LLAMA_CLOUD_API_KEY 가 .env 에 없습니다. LlamaParse 키를 발급하세요.")

    pdf = Path(pdf_path)
    stem = output_stem or pdf.stem
    parser = LlamaParse(api_key=api_key, result_type="markdown", language="ko")
    documents = parser.load_data(str(pdf))
    markdown = "\n\n".join(doc.text for doc in documents)

    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PARSED_DIR / f"{stem}.md"
    out_path.write_text(markdown, encoding="utf-8")
    print(f"parsed {pdf.name} -> {out_path.relative_to(WEEK4_DIR)} ({len(markdown)} chars)")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python parsing/parse_pdf.py <input.pdf> [output_stem]")
        sys.exit(1)
    parse_pdf(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
