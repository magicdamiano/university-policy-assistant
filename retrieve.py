import os
import re
from typing import List, Dict

DOCS_PATH = "docs"

SECTION_RE = re.compile(r"^\d+(\.\d+)*\s+.+")
META_RE = re.compile(
    r"(policy name:|policy reference:|approval authority:|last approved:|review frequency:|page \d+)",
    re.IGNORECASE,
)

IMPORTANT_TERMS = {
    "must", "will", "required", "not permitted", "may", "shall", "deadline",
    "appeal", "withdrawal", "attendance", "engagement", "misconduct"
}


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_documents() -> List[Dict]:
    documents = []

    for filename in os.listdir(DOCS_PATH):
        if not filename.endswith(".txt"):
            continue

        policy_name = filename.replace("_", " ").replace(".txt", "")
        path = os.path.join(DOCS_PATH, filename)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]

        current_title = "General"
        current_section = []

        for line in lines:
            if SECTION_RE.match(line):
                if current_section:
                    documents.append({
                        "policy": policy_name,
                        "section": current_title,
                        "text": normalise(" ".join(current_section))
                    })
                    current_section = []

                current_title = line
                continue

            if META_RE.search(line):
                continue

            current_section.append(line)

        if current_section:
            documents.append({
                "policy": policy_name,
                "section": current_title,
                "text": normalise(" ".join(current_section))
            })

    print(f"[load_docs] Loaded {len(documents)} section-level chunks")
    return documents


DOCUMENTS = load_documents()


def retrieve(question: str, max_results: int = 6) -> List[Dict]:
    q = question.lower()
    q_tokens = set(re.findall(r"\w+", q))

    scored = []

    for d in DOCUMENTS:
        text = d["text"].lower()
        section = d["section"].lower()
        policy = d["policy"].lower()

        tokens = set(re.findall(r"\w+", text))
        overlap = q_tokens & tokens
        if not overlap:
            continue

        score = len(overlap)

        if any(t in text for t in IMPORTANT_TERMS):
            score += 3

        if any(t in section for t in q_tokens):
            score += 2

        if "safeguarding" in policy and not any(
            k in q for k in ["safeguarding", "welfare", "risk", "abuse"]
        ):
            score -= 6

        if "framework" in policy and not any(
            k in q for k in ["framework", "board", "governance"]
        ):
            score -= 4

        scored.append((score, d))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:max_results]]
