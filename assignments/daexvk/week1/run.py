from pathlib import Path

from langchain_core.messages import HumanMessage

from graph import graph


TEST_QUESTIONS = [
    "무사 1,2루에서 내야 뜬공이 나왔는데 인필드 플라이야?",
    "보크가 정확히 무슨 뜻이야?",
    "좋은 야구 규칙 설명을 하려면 어떤 정보부터 확인해야 해?",
    "플라이가 잡히기 전에 3루 주자가 먼저 출발하면 어떻게 돼?",
]


def run_question(question: str) -> dict:
    result = graph.invoke(
        {
            "messages": [HumanMessage(content=question)],
            "final_response": None,
        }
    )
    return result["final_response"].model_dump()


def write_graph_png() -> None:
    graph_view = graph.get_graph()
    try:
        png = graph_view.draw_mermaid_png()
        Path("graph.png").write_bytes(png)
    except Exception as exc:
        Path("graph.mmd").write_text(graph_view.draw_mermaid(), encoding="utf-8")
        print(f"PNG rendering failed; wrote Mermaid source to `graph.mmd` instead. ({exc})")


def main() -> None:
    write_graph_png()

    print("# Baseball Rules ReAct Graph Test Summary\n")
    print("Graph visualization: `graph.png` or fallback `graph.mmd`\n")
    print("| Question | Tools Used | Ruling | Confidence |")
    print("|---|---|---|---|")
    for question in TEST_QUESTIONS:
        response = run_question(question)
        tools = ", ".join(response["used_tools"]) if response["used_tools"] else "None"
        print(
            f"| {question} | {tools} | {response['ruling']} | {response['confidence']} |"
        )


if __name__ == "__main__":
    main()
