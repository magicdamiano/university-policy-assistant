import os
import re
from typing import List, Dict

DOCS_DIR = "docs"
PDF_DIR = "static/policies"

STOPWORDS = {
    "how", "what", "when", "can", "do", "i", "my", "is",
    "the", "a", "an", "to", "of", "and", "in", "for",
    "university", "student", "students"
}

INTENT_KEYWORDS = {
    "complaint": {"complaint", "complaints", "appeal"},
    "misconduct": {"misconduct", "disciplinary", "behaviour"},
    "safety": {"knife", "weapon", "safety", "safeguard", "threat"},
    "attendance": {"attendance", "absence", "engagement"},
    "assessment": {"exam", "assessment", "fail", "resit"},
}


def tokenize(text: str) -> set:
    return {
        t.lower()
        for t in re.findall(r"[a-zA-Z]{3,}", text)
        if t.lower() not in STOPWORDS
    }


def detect_intent(question: str) -> str | None:
    q = question.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in q for k in keywords):
            return intent
    return None


def guess_pdf_name(txt_name: str) -> str:
    return txt_name.replace("_raw.txt", ".pdf").replace(".txt", ".pdf")


def extract_metadata(filename: str, text: str) -> Dict:
    meta = {
        "policy_title": filename.replace("_", " ").replace(".txt", "").title(),
        "policy_code": None,
        "effective_date": None,
        "pdf_link": None
    }

    code = re.search(r"\bQA\s?\d{2,3}\b", text)
    if code:
        meta["policy_code"] = code.group(0)

    year = re.search(r"\b20\d{2}\b", text)
    if year:
        meta["effective_date"] = year.group(0)

    pdf_name = guess_pdf_name(filename)
    pdf_path = os.path.join(PDF_DIR, pdf_name)
    if os.path.exists(pdf_path):
        meta["pdf_link"] = f"/static/policies/{pdf_name}"

    return meta


def load_documents() -> List[Dict]:
    docs = []

    for fname in os.listdir(DOCS_DIR):
        if not fname.endswith(".txt"):
            continue

        path = os.path.join(DOCS_DIR, fname)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        meta = extract_metadata(fname, text)

        for line in text.splitlines():
            line = line.strip()
            if len(line) < 40:
                continue

            docs.append({
                "source": fname,
                "text": line,
                "meta": meta
            })

    return docs


DOCUMENTS = load_documents()


def retrieve(question: str, max_results: int = 20) -> List[Dict]:
    query_tokens = tokenize(question)
    if not query_tokens:
        return []

    intent = detect_intent(question)
    results = []

    for d in DOCUMENTS:
        text_tokens = tokenize(d["text"])
        overlap = query_tokens & text_tokens

        if not overlap:
            continue

        score = len(overlap)

        # intent boost
        if intent:
            if intent in d["source"].lower():
                score += 2
            if any(k in d["text"].lower() for k in INTENT_KEYWORDS[intent]):
                score += 1

        results.append((score, d))

    results.sort(key=lambda x: x[0], reverse=True)

    seen = set()
    output = []

    for _, d in results:
        key = (d["source"], d["text"][:80])
        if key in seen:
            continue
        seen.add(key)
        output.append(d)
        if len(output) >= max_results:
            break

    return output
