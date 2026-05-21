import re
from html.parser import HTMLParser
from urllib.error import URLError
from urllib.request import Request, urlopen

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
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except (ValueError, URLError, TimeoutError) as exc:
        return f"공연 페이지를 가져오지 못했습니다. url={url}, error={exc}"

    parser = _VisibleTextParser()
    parser.feed(html)
    return _compact_text(parser.text())


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
    extract_concert_program,
    retrieve_work_overview,
    retrieve_creation_background,
    retrieve_concert_listening_points,
    retrieve_preview_keywords,
]
