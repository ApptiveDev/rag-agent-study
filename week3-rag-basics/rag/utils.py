import os
import pprint
import uuid
from typing import Literal

from langchain_core.messages import BaseMessage, convert_to_messages, get_buffer_string
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class RelevanceScore(BaseModel):
    score: Literal["yes", "no"] = Field(
        description="Whether the retrieved context is relevant to the question."
    )


def setup_langsmith(project_name):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = project_name
    os.environ["LANGSMITH_PROJECT"] = project_name
    os.environ.setdefault("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")


def messages_to_history(messages):
    if not messages:
        return ""

    try:
        return get_buffer_string(convert_to_messages(messages))
    except Exception:
        history = []
        for message in messages:
            if isinstance(message, BaseMessage):
                role = message.type
                content = message.content
            elif isinstance(message, dict):
                role = message.get("role") or message.get("type", "message")
                content = message.get("content", "")
            elif isinstance(message, (tuple, list)) and len(message) >= 2:
                role, content = message[0], message[1]
            else:
                role, content = "message", str(message)
            history.append(f"{role}: {_content_to_text(content)}")
        return "\n".join(history)


def random_uuid():
    return str(uuid.uuid4())


def visualize_graph(graph):
    graph_view = graph.get_graph()
    try:
        from IPython.display import Image, display

        display(Image(graph_view.draw_mermaid_png()))
    except Exception:
        print(graph_view.draw_mermaid())


def invoke_graph(graph, inputs, config=None, context=None, node_names=None):
    if context is None:
        result = graph.invoke(inputs, config)
    else:
        result = graph.invoke(inputs, config, context=context)

    if node_names:
        _print_node_values(result, node_names)
    else:
        _print_final_result(result)

    return result


def stream_graph(graph, inputs, config=None, context=None, node_names=None, callback=None):
    try:
        stream = graph.stream(
            inputs,
            config,
            context=context,
            stream_mode="messages",
        )
        for chunk_msg, metadata in stream:
            node = metadata.get("langgraph_node", "")
            if node_names and node not in node_names:
                continue

            content = _content_to_text(getattr(chunk_msg, "content", chunk_msg))
            if not content:
                continue

            args = {"node": node, "content": content, "message": chunk_msg, "metadata": metadata}
            if callback:
                callback(args)
            else:
                print(content, end="", flush=True)
        if callback is None:
            print()
    except TypeError:
        _stream_updates(graph, inputs, config, context, node_names, callback)


def create_retrieval_relevance_chain(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a grader assessing whether retrieved context is relevant "
                "to a user question. Return 'yes' if the context contains "
                "information useful for answering the question. Otherwise return 'no'.",
            ),
            (
                "human",
                "Question:\n{question}\n\nRetrieved context:\n{context}",
            ),
        ]
    )
    return prompt | llm.with_structured_output(RelevanceScore)


def format_tavily_results(search_result):
    results = search_result.get("results", [])
    return "\n".join(
        [
            (
                f"<document><title>{doc.get('title', '')}</title>"
                f"<content>{doc.get('content', '')}</content>"
                f"<source>{doc.get('url', '')}</source></document>"
            )
            for doc in results
        ]
    )


def _stream_updates(graph, inputs, config, context, node_names, callback):
    if context is None:
        stream = graph.stream(inputs, config)
    else:
        stream = graph.stream(inputs, config, context=context)

    for update in stream:
        if not isinstance(update, dict):
            pprint.pp(update)
            continue

        for node, value in update.items():
            if node_names and node not in node_names:
                continue
            content = _content_to_text(value)
            if callback:
                callback({"node": node, "content": content, "value": value})
            else:
                print(f"\n[{node}]")
                print(content)


def _print_final_result(result):
    if isinstance(result, dict):
        if "answer" in result:
            print(_content_to_text(result["answer"]))
            return
        if "messages" in result and result["messages"]:
            print(_content_to_text(result["messages"][-1]))
            return

    pprint.pp(result)


def _print_node_values(result, node_names):
    if not isinstance(result, dict):
        pprint.pp(result)
        return

    printed = False
    for node_name in node_names:
        if node_name in result:
            print(f"\n[{node_name}]")
            print(_content_to_text(result[node_name]))
            printed = True

    if not printed:
        _print_final_result(result)


def _content_to_text(content):
    if isinstance(content, BaseMessage):
        return _content_to_text(content.content)
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        if "content" in content:
            return _content_to_text(content["content"])
        if "text" in content:
            return str(content["text"])
        return pprint.pformat(content)
    if isinstance(content, list):
        return "".join(_content_to_text(item) for item in content)
    return str(content)


def format_docs(docs):
    return "\n".join(
        [
            f"<document><content>{doc.page_content}</content><source>{doc.metadata['source']}</source><page>{int(doc.metadata['page'])+1}</page></document>"
            for doc in docs
        ]
    )


def format_searched_docs(docs):
    return "\n".join(
        [
            f"<document><content>{doc['content']}</content><source>{doc['url']}</source></document>"
            for doc in docs
        ]
    )


def format_task(tasks):
    # 결과를 저장할 빈 리스트 생성
    task_time_pairs = []

    # 리스트를 순회하면서 각 항목을 처리
    for item in tasks:
        # 콜론(:) 기준으로 문자열을 분리
        task, time_str = item.rsplit(":", 1)
        # '시간' 문자열을 제거하고 정수로 변환
        time = int(time_str.replace("시간", "").strip())
        # 할 일과 시간을 튜플로 만들어 리스트에 추가
        task_time_pairs.append((task, time))

    # 결과 출력
    return task_time_pairs
