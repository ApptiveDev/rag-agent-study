from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_core.messages import HumanMessage
from graph import build_graph


app = build_graph()

config = {
  "configurable": {
    "thread_id" : "react-thread"
  }
}

inputs = [
  "long polling 관련 사례 찾아줘",
  "방금 말한 그 사례는 구조/단순 버그 문제 중에 어디에 속할까?",
  "네가 말한 그 관점으로 사례를 다시 정리해줘"
]

for text in inputs:
  result = app.invoke(
    {"messages": [HumanMessage(content=text)]},
    config = config,
  )
  
  print("\n--- latteeea ---")
  print(text)
  
  print("\n--- AI ---")
  print(result["messages"][-1])