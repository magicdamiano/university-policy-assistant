def ask_agent(question, sources):
    if not sources:
        return "No relevant information was found in the regulations."

    answer = f"Question:\n{question}\n\nRelevant regulatory statements:\n"

    for i, s in enumerate(sources, start=1):
        answer += f"{i}. {s['text']}\n"

    answer += "\nThis answer is based only on the university regulatory documents."

    return answer
