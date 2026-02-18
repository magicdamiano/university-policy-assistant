import os

DOCS_DIR = "docs"

def retrieve(question, max_results=6):
    question_lower = question.lower()
    results = []

    for filename in os.listdir(DOCS_DIR):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(DOCS_DIR, filename)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                clean = line.strip()
                if len(clean) < 40:
                    continue

                if any(word in clean.lower() for word in question_lower.split()):
                    results.append({
                        "source": filename,
                        "text": clean
                    })

    return results[:max_results]
