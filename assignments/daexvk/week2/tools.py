import base64
import mimetypes
import os
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool


class _VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip = False
        self._chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"}:
            self._skip = False

    def handle_data(self, data):
        text = data.strip()
        if not self._skip and text:
            self._chunks.append(text)

    def text(self) -> str:
        return "\n".join(self._chunks)


def _compact_text(text: str, limit: int = 8000) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]


def _fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8", errors="ignore")


def _load_project_env() -> None:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(env_path, override=False)


def _fetch_bytes(url: str, limit: int = 5_000_000) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=15) as response:
        content_type = response.headers.get("content-type", "").split(";")[0].strip()
        data = response.read(limit + 1)

    if len(data) > limit:
        raise ValueError(f"image is too large: {url}")

    if not content_type:
        content_type = mimetypes.guess_type(url)[0] or "image/jpeg"

    return data, content_type


def _extract_attr_values(html: str, attr_name: str) -> list[str]:
    pattern = re.compile(rf"""{attr_name}=["']([^"']+)["']""", re.IGNORECASE)
    return [unescape(value.strip()) for value in pattern.findall(html) if value.strip()]


def _extract_image_urls(html: str, base_url: str, limit: int = 6) -> list[str]:
    raw_candidates = []

    meta_pattern = re.compile(
        r"""<meta\b[^>]*(?:property|name)=["'](?:og:image|twitter:image)["'][^>]*content=["']([^"']+)["'][^>]*>""",
        re.IGNORECASE,
    )
    raw_candidates.extend(unescape(value.strip()) for value in meta_pattern.findall(html))

    for attr_name in ("src", "data-src", "data-original", "data-lazy-src"):
        raw_candidates.extend(_extract_attr_values(html, attr_name))

    for srcset in _extract_attr_values(html, "srcset"):
        raw_candidates.extend(part.strip().split(" ")[0] for part in srcset.split(",") if part.strip())

    background_pattern = re.compile(r"""background-image\s*:\s*url\((["']?)(.*?)\1\)""", re.IGNORECASE)
    raw_candidates.extend(unescape(value.strip()) for _, value in background_pattern.findall(html))

    image_urls = []
    for candidate in raw_candidates:
        if not candidate or candidate.startswith("data:"):
            continue

        absolute_url = urljoin(base_url, candidate)
        lowered = absolute_url.lower()
        if any(skip in lowered for skip in ("logo", "icon", "favicon", "spinner", "blank")):
            continue
        if any(lowered.split("?", 1)[0].endswith(ext) for ext in (".js", ".css", ".woff", ".woff2", ".ttf")):
            continue
        if absolute_url not in image_urls:
            image_urls.append(absolute_url)

    def priority(image_url: str) -> tuple[int, str]:
        lowered = image_url.lower()
        score = 0
        if any(token in lowered for token in ("poster", "performance", "/down/", "/upload/", "/rent/", "concert")):
            score -= 2
        if any(token in lowered for token in ("sns", "share", "banner")):
            score += 2
        return score, image_url

    return sorted(image_urls, key=priority)[:limit]


def _ocr_poster_image(image_url: str, image_bytes: bytes, content_type: str, page_text: str, metadata: str) -> str:
    _load_project_env()
    model_name = os.getenv("CLASSICAL_POSTER_OCR_MODEL", os.getenv("CLASSICAL_AGENT_MODEL", "openai:gpt-5.4-mini"))
    vision_model = init_chat_model(model_name)
    image_data = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:{content_type};base64,{image_data}"

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "이 이미지는 클래식 공연 상세 페이지의 포스터일 수 있습니다. "
                    "이미지 안의 텍스트를 읽되, raw OCR 로그를 나열하지 말고 사용자가 바로 볼 수 있는 공연 정보로 정리하세요. "
                    "주변 페이지 텍스트와 이미지 메타데이터도 함께 참고해서 포스터에서 잘 안 읽히는 부분을 보완하세요. "
                    "반드시 다음 항목만 간결하게 구분하세요: 공연명, 일시, 장소, 출연진, 프로그램/곡명, 예습에 필요한 핵심 요약, 불확실한 정보. "
                    "확실하지 않은 내용은 추정하지 말고 '불확실한 정보'에 넣으세요. "
                    f"\n\n이미지 URL: {image_url}"
                    f"\n\n이미지 메타데이터:\n{metadata or '없음'}"
                    f"\n\n주변 페이지 텍스트:\n{page_text or '없음'}"
                ),
            },
            {"type": "image_url", "image_url": {"url": data_url}},
        ]
    )

    response = vision_model.invoke([message])
    return str(response.content)


def _score_documents(query: str, documents: list[dict]) -> list[dict]:
    query_terms = set(re.findall(r"[A-Za-z가-힣0-9]+", query.lower()))
    scored = []

    for document in documents:
        haystack = f"{document['title']} {document['content']}".lower()
        score = sum(1 for term in query_terms if term in haystack)
        scored.append((score, document))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [document for score, document in scored if score > 0][:3] or documents[:2]


def _format_documents(query: str, documents: list[dict]) -> str:
    selected = _score_documents(query, documents)
    return "\n\n".join(
        f"[source: {document['source']}]\n"
        f"title: {document['title']}\n"
        f"{document['content']}"
        for document in selected
    )


WORK_OVERVIEW_DOCS = [
    {
        "title": "Mahler Symphony No. 5 beginner overview",
        "source": "local-rag:mahler-5-overview",
        "content": (
            "말러 교향곡 5번은 다섯 악장으로 된 대규모 교향곡이다. 어둡고 장례 행진 같은 "
            "출발에서 격렬한 투쟁, 고요한 사랑의 노래 같은 아다지에토, 밝은 피날레로 나아간다. "
            "초보자는 전체를 하나의 감정 여행처럼 듣는 것이 좋다."
        ),
    },
    {
        "title": "Beethoven Symphony No. 5 beginner overview",
        "source": "local-rag:beethoven-5-overview",
        "content": (
            "베토벤 교향곡 5번은 짧은 네 음 동기로 시작하는 대표적인 교향곡이다. 긴장과 투쟁의 "
            "느낌에서 마지막 악장의 밝은 승리감으로 향하는 흐름이 뚜렷하다."
        ),
    },
    {
        "title": "Classical concert beginner overview",
        "source": "local-rag:concert-prep-overview",
        "content": (
            "처음 클래식 공연을 볼 때는 모든 형식을 분석하려 하기보다 작품의 분위기, 반복되는 선율, "
            "악기 색채, 큰 감정 변화에 집중하면 공연을 더 쉽게 따라갈 수 있다."
        ),
    },
]

BACKGROUND_DOCS = [
    {
        "title": "Mahler Symphony No. 5 creation background",
        "source": "local-rag:mahler-5-background",
        "content": (
            "말러 교향곡 5번은 말러의 중기 양식을 대표하는 작품으로, 성악 없이 순수 관현악으로 "
            "구성되어 있다. 개인적 위기와 회복, 알마와의 만남을 둘러싼 시기와 자주 연결해 설명된다. "
            "다만 각 악장을 단일한 줄거리로 고정해 해석하는 것은 조심해야 한다."
        ),
    },
    {
        "title": "Beethoven Symphony No. 5 creation background",
        "source": "local-rag:beethoven-5-background",
        "content": (
            "베토벤 교향곡 5번은 베토벤이 청력 악화와 창작적 전환을 겪던 시기의 작품이다. 흔히 "
            "'운명'이라는 이미지로 설명되지만, 이 표제는 작품 이해를 돕는 별칭에 가깝다."
        ),
    },
]

LISTENING_POINT_DOCS = [
    {
        "title": "Mahler Symphony No. 5 listening points",
        "source": "local-rag:mahler-5-listening",
        "content": (
            "말러 5번에서는 1악장의 트럼펫 신호와 장례 행진 리듬, 2악장의 격렬한 폭발, 3악장의 "
            "왈츠적 움직임, 4악장 아다지에토의 현악기와 하프, 5악장의 밝고 복잡한 피날레를 "
            "중심으로 들으면 좋다."
        ),
    },
    {
        "title": "Beethoven Symphony No. 5 listening points",
        "source": "local-rag:beethoven-5-listening",
        "content": (
            "베토벤 5번은 첫 네 음 동기가 작품 전체에서 어떻게 변형되는지, 어두운 1악장에서 "
            "밝은 4악장으로 분위기가 어떻게 전환되는지에 집중하면 좋다."
        ),
    },
]


@tool
def fetch_concert_page(url: str) -> str:
    """Fetch visible text from a concert detail page URL."""
    try:
        html = _fetch_html(url)
    except (ValueError, URLError, TimeoutError) as exc:
        return f"공연 페이지를 가져오지 못했습니다. url={url}, error={exc}"

    parser = _VisibleTextParser()
    parser.feed(html)
    return _compact_text(parser.text())


@tool
def extract_poster_image_text(url: str) -> str:
    """Extract poster image details and return a cleaned concert-info summary."""
    try:
        html = _fetch_html(url)
    except (ValueError, URLError, TimeoutError) as exc:
        return f"포스터 이미지 정보를 가져오지 못했습니다. url={url}, error={exc}"

    parser = _VisibleTextParser()
    parser.feed(html)
    page_text = _compact_text(parser.text(), limit=3000)

    image_pattern = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
    attr_pattern = re.compile(r"""(alt|title|src|data-src|aria-label)=["']([^"']+)["']""", re.IGNORECASE)

    poster_rows = []
    for index, tag in enumerate(image_pattern.findall(html), start=1):
        attrs = {key.lower(): unescape(value.strip()) for key, value in attr_pattern.findall(tag)}
        haystack = " ".join(attrs.values()).lower()
        if not attrs or ("poster" not in haystack and "포스터" not in haystack and "performance" not in haystack and index > 5):
            continue

        poster_rows.append(
            "\n".join(
                [
                    f"image_candidate: {index}",
                    f"alt: {attrs.get('alt', '')}",
                    f"title: {attrs.get('title', '')}",
                    f"src: {attrs.get('src') or attrs.get('data-src', '')}",
                ]
            )
        )

    image_urls = _extract_image_urls(html, url)
    metadata = "\n\n".join(poster_rows[:5])
    successful_results = []
    failure_notes = []
    for image_url in image_urls[:3]:
        try:
            image_bytes, content_type = _fetch_bytes(image_url)
        except (ValueError, URLError, TimeoutError) as exc:
            failure_notes.append(f"{image_url}: 이미지를 가져오지 못했습니다: {exc}")
            continue

        if not content_type.startswith("image/"):
            failure_notes.append(f"{image_url}: 이미지 content-type이 아닙니다: {content_type}")
            continue

        try:
            ocr_text = _ocr_poster_image(image_url, image_bytes, content_type, page_text, metadata)
        except Exception as exc:
            failure_notes.append(f"{image_url}: 비전 OCR에 실패했습니다: {type(exc).__name__}: {exc}")
            continue

        successful_results.append((image_url, ocr_text))
        break

    if successful_results:
        image_url, summary = successful_results[0]
        return _compact_text(
            "\n".join(
                [
                    "[포스터 기반 공연 정보 정리]",
                    summary,
                    "",
                    f"참고 이미지: {image_url}",
                    "참고: 포스터 이미지와 주변 페이지 텍스트를 함께 사용해 정리했습니다.",
                ]
            ),
            limit=8000,
        )

    if not poster_rows and not failure_notes:
        return "포스터 이미지 후보를 찾지 못했습니다. 페이지가 스크립트로 이미지를 동적으로 불러올 수 있습니다."

    sections = ["포스터 OCR을 완료하지 못했습니다. 확인 가능한 주변 정보만 정리합니다."]
    if page_text:
        sections.append("[주변 페이지 텍스트]\n" + page_text)
    if poster_rows:
        sections.append("[이미지 메타데이터]\n" + "\n\n".join(poster_rows[:3]))
    if failure_notes:
        sections.append("[처리 상태]\n" + "\n".join(f"- {note}" for note in failure_notes[:3]))

    return _compact_text("\n\n".join(sections), limit=6000)


@tool
def extract_concert_program(page_text: str) -> str:
    """Extract likely concert title, date, venue, performers, and program lines from concert page text."""
    lines = [line.strip() for line in page_text.splitlines() if line.strip()]
    title = lines[0] if lines else "unknown"

    date_pattern = re.compile(r"\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}")
    program_pattern = re.compile(
        r"(symphony|concerto|sonata|quartet|overture|교향곡|협주곡|소나타|서곡|모음곡|아다지에토|말러|베토벤|브람스|차이콥스키|모차르트)",
        re.IGNORECASE,
    )
    performer_pattern = re.compile(r"(지휘|연주|협연|오케스트라|필하모닉|교향악단|Conductor|Orchestra|Soloist)", re.IGNORECASE)

    dates = [line for line in lines if date_pattern.search(line)][:3]
    performers = [line for line in lines if performer_pattern.search(line)][:8]
    program_lines = [line for line in lines if program_pattern.search(line)][:12]

    return _compact_text(
        "\n".join(
            [
                f"title: {title}",
                f"dates: {dates}",
                f"performers: {performers}",
                "program_candidates:",
                *program_lines,
            ]
        )
    )


@tool
def retrieve_work_overview(query: str) -> str:
    """Retrieve beginner-friendly overview documents about a classical work."""
    return _format_documents(query, WORK_OVERVIEW_DOCS)


@tool
def retrieve_creation_background(query: str) -> str:
    """Retrieve historical, personal, and artistic background documents about a classical work."""
    return _format_documents(query, BACKGROUND_DOCS)


@tool
def retrieve_concert_listening_points(query: str) -> str:
    """Retrieve beginner-friendly listening points for hearing a classical work in concert."""
    return _format_documents(query, LISTENING_POINT_DOCS)


@tool
def retrieve_preview_keywords(query: str) -> str:
    """Return YouTube or web search keywords for preview listening before a concert."""
    base_query = query.strip()
    if not base_query:
        base_query = "클래식 공연 예습"

    keywords = [
        f"{base_query} 초보자 해설",
        f"{base_query} 감상 포인트",
        f"{base_query} beginner guide",
        f"{base_query} live performance",
    ]

    return "\n".join(f"- {keyword}" for keyword in keywords)


ALL_TOOLS = [
    fetch_concert_page,
    extract_poster_image_text,
    extract_concert_program,
    retrieve_work_overview,
    retrieve_creation_background,
    retrieve_concert_listening_points,
    retrieve_preview_keywords,
]
