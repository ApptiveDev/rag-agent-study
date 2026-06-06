from langchain_openai import ChatOpenAI


def get_llm(model: str = "gpt-4.1-mini", temperature: float = 0):
    return ChatOpenAI(model=model, temperature=temperature)


def rewrite_question(llm, question: str) -> str:
    prompt = f"""Translate the following Minecraft question into English.

Question:
{question}

Return only the translated question."""
    return llm.invoke(prompt).content.strip()


def answer_question(llm, question: str, context: str) -> str:
    prompt = f"""In Korean,
Answer the question using ONLY the provided context.

Context:
{context}

Question:
{question}"""
    return llm.invoke(prompt).content
