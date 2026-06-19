from pydantic import BaseModel, Field

class AgentResponse(BaseModel):
  answer: str = Field(description="질문에 대한 에이전트 답변")
  used_tools: list[str] = Field(description="응답 생성 시 사용한 tool 목록")
  evidence: list[str] = Field(description="답변 근거가 된 노트(노션)")
  confidence: list[str] = Field(description="0.0~1.0 사이의 llm이 부여한 신뢰도")