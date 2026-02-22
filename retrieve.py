import re
from typing import List, Dict
from load_docs import load_documents

DOCUMENTS = load_documents()

WORD_RE = re.compile(r"[a-zA-Z]{3,}")


def tokenize(text: str) -> set:
    return set(w.lower() for w in WORD_RE.findall(text))


# -------------------------------
# INTENT DETECTION
# -------------------------------

INTENT_KEYWORDS = {
    "complaint": [
        "complaint", "complain", "complaints", "grievance"
    ],
    "appeal": [
        "appeal", "appeals"
    ],
    "misconduct": [
        "misconduct", "discipline", "plagiarism"
    ],
    "attendance": [
        "attendance", "engagement", "absence"
    ],
    "withdrawal": [
        "withdraw", "withdrawal", "leave"
    ],
}


def detect_intent(question: str) -> str | None:
    q = question.lower()
    for intent, keys in INTENT_KEYWORDS.items():
        if any(k in q for k in keys):
            return intent
    return None


# -------------------------------
# RETRIEVAL
# -------------------------------

def retrieve(question: str, max_results: int = 8) -> List[Dict]:
    q_tokens = tokenize(question)
    if not q_tokens:
        return []

    intent = detect_intent(question)
    scored = []

    for d in DOCUMENTS:
        text = d["text"].lower()
        source = d["source"].lower()
        policy = d["policy"].lower()

        # Intent filtering (HARD FILTER)
        if intent:
            if intent == "complaint":
                if "complaint" not in source and "complaint" not in policy:
                    continue

        text_tokens = tokenize(text)
        overlap = q_tokens & text_tokens

        if not overlap:
            continue

        score = len(overlap)

        # Section relevance
        score += len(q_tokens & tokenize(d["section"]))

        scored.append((score, d))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    seen = set()

    for _, d in scored:
        key = (d["policy"], d["section"])
        if key in seen:
            continue
        seen.add(key)
        results.append(d)
        if len(results) >= max_results:
            break

    return results
