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

result = app.invoke({
  "messages": [
    HumanMessage(content="React 사례 찾아줘")
  ]
},
config = config)

for msg in result["messages"]:
  print(msg)