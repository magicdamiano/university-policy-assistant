import os
import re
from typing import List, Dict

DOCS_DIR = "docs"

SECTION_PATTERN = re.compile(
    r"^(section|chapter|part)?\s*\d+(\.\d+)*\s*[-–:]?\s+.+",
    re.IGNORECASE
)


def detect_sections(text: str) -> List[Dict]:
    """
    Splits a document into section-aware chunks.
    """
    lines = text.splitlines()
    chunks = []

    current_title = "General"
    buffer = []

    for line in lines:
        clean = line.strip()

        if not clean:
            continue

        if SECTION_PATTERN.match(clean):
            if buffer:
                chunks.append({
                    "section": current_title,
                    "text": " ".join(buffer).strip()
                })
                buffer = []

            current_title = clean
        else:
            buffer.append(clean)

    if buffer:
        chunks.append({
            "section": current_title,
            "text": " ".join(buffer).strip()
        })

    return chunks


def load_documents() -> List[Dict]:
    documents = []

    for fname in os.listdir(DOCS_DIR):
        if not fname.endswith(".txt"):
            continue

        path = os.path.join(DOCS_DIR, fname)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()

        policy_name = fname.replace(".txt", "").replace("_", " ").title()

        sections = detect_sections(raw_text)

        for sec in sections:
            if len(sec["text"]) < 200:
                continue

            documents.append({
                "policy": policy_name,
                "section": sec["section"],
                "text": sec["text"],
                "source": fname
            })

    print(f"[load_docs] Loaded {len(documents)} chunks")
    return documents
