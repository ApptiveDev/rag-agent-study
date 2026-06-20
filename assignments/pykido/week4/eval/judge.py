import os
import sys

from dotenv import find_dotenv, load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import JudgeScore

load_dotenv(find_dotenv(), override=True)
os.environ["LANGSMITH_TRACING"] = "false"

JUDGE_SYSTEM = """당신은 RAG 답변을 채점하는 엄격하고 공정한 평가자입니다.
두 축을 각각 1~5점으로 매기세요.

- correctness: 답이 reference answer 와 의미적으로 일치하는 정도.
  1=완전히 틀림, 3=부분적으로 맞음, 5=핵심이 정확히 일치.
- groundedness: 답이 검색된 context 문서에 근거하는 정도.
  1=context 에 없는 내용을 지어냄(환각), 5=모든 주장이 context 로 뒷받침됨.

특수 규칙:
- 질문이 지식베이스 밖이라 정답 문서가 없는 경우(reference 가 '모른다고 답해야 한다'),
  답이 정직하게 '근거가 없어 모른다'고 말했으면 correctness·groundedness 모두 5,
  엉뚱한 내용을 지어냈으면 둘 다 1~2 로 채점합니다.
reason 은 한 줄로 간단히 적습니다."""

judge_model = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(JudgeScore)


def judge_answer(question: str, reference: str, answer: str, context: str) -> JudgeScore:
    human = (
        f"[질문]\n{question}\n\n"
        f"[reference answer]\n{reference}\n\n"
        f"[검색된 context]\n{context}\n\n"
        f"[채점 대상 답변]\n{answer}"
    )
    return judge_model.invoke([SystemMessage(content=JUDGE_SYSTEM), HumanMessage(content=human)])
