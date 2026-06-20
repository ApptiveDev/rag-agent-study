from dotenv import load_dotenv

load_dotenv(override=True)

from graph import run_agentic_rag


QUESTIONS = [
    "Cursor가 왜 멍청해 보였는지 인과적으로 설명해줘",
]

for question in QUESTIONS:
    result = run_agentic_rag(question=question, strategy="markdown")

    print("\n--- latteeea week4 ---")
    print(f"Question: {result['question']}")
    print(f"Rewritten: {result['rewritten_question']} (count={result['rewrite_count']})")
    print("-" * 80)
    print(result["answer"])
    print("-" * 80)
    print("Sources:")
    for source in result["sources"]:
        print(f"- {source['filename']} | {source['chunk_id']}")
