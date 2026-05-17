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
  "React 사례 찾아줘",
  "아까 그 사례 다시 설명해줘",
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