from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_core.messages import HumanMessage
from graph import build_graph
from langgraph.types import Command


app = build_graph()

config = {
  "configurable": {
    "thread_id" : "week2-interrupt-thread"
  }
}

inputs = [
  "long polling 관련 사례를 글로 만들어줘",
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

result = app.invoke(
  Command(resume="2"),
  config = config,
)

print("\n--- INTERRUPT TEST ---")
print("Agent asked for narrative direction.")
print("Resume with choice: 2")

print(result["messages"][-1])
print("narrative_intent:", result.get("narrative_intent"))