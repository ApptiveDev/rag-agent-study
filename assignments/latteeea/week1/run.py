from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_core.messages import HumanMessage
from graph import build_graph


app = build_graph()

result = app.invoke({
  "messages": [
    HumanMessage(content="longpolling 이 뭔지 설명해줘")
  ]
})

for msg in result["messages"]:
  print(msg)