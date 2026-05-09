import re
from urllib.parse import parse_qs, urlparse

import requests
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from youtube_transcript_api import YouTubeTranscriptApi

from schema import QuizResult, SummaryResult, TranscriptResult

_summarizer = init_chat_model("gpt-5.4-mini").with_structured_output(SummaryResult)
_quiz_generator = init_chat_model("gpt-5.4-mini").with_structured_output(QuizResult)


def _extract_video_id(url: str) -> str:
    """YouTube URL에서 video_id를 추출한다.

    youtu.be 단축 링크, watch?v=, shorts/, embed/ 등 주요 포맷을 지원.
    이미 video_id 자체가 들어온 경우(11자 영숫자)도 그대로 통과시킨다.
    """
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url

    parsed = urlparse(url)

    if parsed.hostname in {"youtu.be"}:
        return parsed.path.lstrip("/").split("/")[0]

    if parsed.hostname and "youtube.com" in parsed.hostname:
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            if "v" in qs:
                return qs["v"][0]
        # /shorts/<id>, /embed/<id>, /v/<id>
        match = re.match(r"^/(shorts|embed|v)/([A-Za-z0-9_-]{11})", parsed.path)
        if match:
            return match.group(2)

    raise ValueError(f"YouTube URL에서 video_id를 추출할 수 없습니다: {url}")


def _fetch_video_title(video_id: str) -> str:
    """YouTube oEmbed 엔드포인트로 영상 제목만 가볍게 조회."""
    try:
        response = requests.get(
            "https://www.youtube.com/oembed",
            params={
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "format": "json",
            },
            timeout=5,
        )
        response.raise_for_status()
        return response.json().get("title", f"(제목 없음 · {video_id})")
    except Exception:
        return f"(제목 조회 실패 · {video_id})"


@tool
def fetch_video_transcript(url: str) -> dict:
    """YouTube 영상 URL을 받아 자막과 영상 제목을 반환합니다.

    한국어 자막을 우선 시도하고 없으면 영어 자막을 사용합니다. 자막이 전혀 없는
    영상이면 에러 메시지를 반환합니다. 사용자가 학습하고 싶은 영상 URL을 보냈을 때
    가장 먼저 호출해야 합니다.
    """
    try:
        video_id = _extract_video_id(url)
    except ValueError as exc:
        return {"error": str(exc)}

    try:
        fetched = YouTubeTranscriptApi().fetch(video_id, languages=("ko", "en"))
    except Exception as exc:
        return {
            "error": (
                f"자막을 가져오지 못했습니다 (video_id={video_id}). "
                f"자막이 비활성화되어 있거나 지원되지 않는 언어일 수 있습니다. 원인: {exc}"
            )
        }

    transcript_text = " ".join(snippet.text for snippet in fetched.snippets).strip()
    if not transcript_text:
        return {"error": f"자막이 비어 있습니다 (video_id={video_id})."}

    result = TranscriptResult(
        video_id=video_id,
        video_title=_fetch_video_title(video_id),
        transcript=transcript_text,
        language=fetched.language_code,
    )
    return result.model_dump()


@tool
def summarize_video(transcript: str, video_title: str = "") -> dict:
    """자막 텍스트를 받아 3~5문장 요약과 핵심 포인트 5개 이내를 생성합니다.

    `fetch_video_transcript`를 먼저 호출해 받은 자막을 그대로 넘기면 됩니다.
    영상 제목을 함께 전달하면 요약 품질이 좋아집니다.
    """
    prompt = (
        "당신은 영상 학습 도우미입니다. 아래 YouTube 영상의 자막을 읽고 "
        "한국어로 다음을 작성하세요.\n"
        "1) summary: 3~5문장의 핵심 요약\n"
        "2) key_points: 학습자가 꼭 기억해야 할 포인트 5개 이내(짧은 문장)\n\n"
        f"[영상 제목]\n{video_title or '(없음)'}\n\n"
        f"[자막]\n{transcript[:12000]}"
    )
    result: SummaryResult = _summarizer.invoke(prompt)
    return result.model_dump()


@tool
def generate_quiz(summary: str, key_points: list[str], num_questions: int = 3) -> dict:
    """요약과 핵심 포인트를 바탕으로 복습용 퀴즈를 생성합니다.

    `summarize_video` 결과를 그대로 넘기면 됩니다. 기본 3문제이며, 사용자가
    더 많은 문제를 원하면 num_questions를 조정할 수 있습니다.
    """
    bullet_points = "\n".join(f"- {p}" for p in key_points)
    prompt = (
        "당신은 학습 동반자입니다. 아래 요약과 핵심 포인트를 바탕으로 "
        f"한국어 복습 퀴즈 {num_questions}개를 만드세요. "
        "각 항목에는 question, answer, explanation을 모두 포함해야 합니다. "
        "단순 암기보다 개념 이해를 묻는 문제를 우선하세요.\n\n"
        f"[요약]\n{summary}\n\n"
        f"[핵심 포인트]\n{bullet_points}"
    )
    result: QuizResult = _quiz_generator.invoke(prompt)
    return result.model_dump()


ALL_TOOLS = [fetch_video_transcript, summarize_video, generate_quiz]
