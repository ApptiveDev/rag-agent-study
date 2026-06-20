"""State 및 최종 응답 스키마 정의."""
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from operator import add


def upsert_skill_choices(current: list[dict], new: list[dict]) -> list[dict]:
    """같은 level 항목이 있으면 교체, 없으면 추가.

    하수구에서 직업을 바꿀 수 있으므로 add 대신 upsert 동작이 필요함.
    """
    result = list(current)
    for incoming in new:
        idx = next((i for i, x in enumerate(result) if x["level"] == incoming["level"]), None)
        if idx is not None:
            result[idx] = incoming
        else:
            result.append(incoming)
    return result


class AgentState(TypedDict):
    """ReAct loop가 공유하는 그래프 상태
    - messages: agent <-> tool 사이를 오가며 누적되는 대화 기록.
      add_messages reducer 덕분에 노드가 새 메세지만 반환해도 자동 append
    - tool_call_trace: 어떤 도구를 어떤 인자로 호출했는지 기록.
    - skill_choices: 스킬 트리 선택 내역. 같은 레벨 재선택 시 upsert.
    """
    messages: Annotated[list[AnyMessage], add_messages]
    tool_call_trace: Annotated[list[dict], add]
    skill_choices: Annotated[list[dict], upsert_skill_choices]


class FinalAnswer(BaseModel):
    """사용자에게 전달되는 최종 응답 형식.

    1주차 과제 필수 사항: structured output 강제
    1주차 과제 심화 사항: 근거 / 사용한 도구 / Confidence 필드 포함
    """
    answer: str = Field(description="사용자 질문에 대한 최종 답변 (한국어)")
    sources_used: list[str] = Field(description="답변 생성에 사용한 도구 이름 목록", default_factory=list,)
    reasoning: str = Field(description="이 답변에 도달한 추론 과정 요약")
    confidence: float = Field(description="답변에 대한 확신도 (0.0~1.0)", ge=0.0, le=1.0)


class SkillChoiceCommit(BaseModel):
    """commit_choice 노드에서 사용자 답변을 파싱하는 스키마."""
    level: int = Field(description="스킬 레벨 (5 또는 10)")
    choice: str = Field(description="선택한 직업 이름 (예: 목축업자, 경작인)")
    is_change: bool = Field(description="기존 선택을 변경하는 건지 여부")