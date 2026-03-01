import os
import re
import math
from typing import List, Dict, Set
from collections import Counter

# ==================================================
# PATHS & COMPILE-TIME PATTERNS
# ==================================================

DOCS_PATH = "docs"

SECTION_RE = re.compile(r"^\d+(\.\d+)*\s+.+")

META_RE = re.compile(
    r"(policy name:|policy reference:|approval authority:|last approved:|review frequency:|page \d+)",
    re.IGNORECASE,
)

# ==================================================
# STOP WORDS  (excluded from scoring entirely)
# ==================================================

STOP_WORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "i", "my", "me",
    "we", "our", "you", "your", "it", "its", "this", "that", "what",
    "which", "who", "how", "when", "where", "why", "not", "no", "so",
    "about", "as", "up", "out", "there", "their", "they", "them",
    "he", "she", "his", "her", "am",
}

# ==================================================
# IMPORTANT TERMS  (must appear in BOTH question and chunk to score)
# ==================================================

IMPORTANT_TERMS: Set[str] = {
    "must", "required", "not permitted", "shall", "deadline",
    "appeal", "withdrawal", "attendance", "engagement", "misconduct",
    "plagiarism", "extension", "mitigating", "extenuating", "resit",
    "resubmission", "suspension", "deferral", "termination",
}

# ==================================================
# OFF-TOPIC POLICY PENALTIES
# policy substring → list of required question keywords to AVOID penalty
# If none of the keywords appear in the question, apply the penalty.
# ==================================================

OFF_TOPIC_PENALTIES: List[Dict] = [
    {"policy": "safeguarding",  "keywords": ["safeguarding", "welfare", "risk", "abuse", "protection"],  "penalty": 8},
    {"policy": "framework",     "keywords": ["framework", "board", "governance", "committee"],           "penalty": 6},
    {"policy": "staff",         "keywords": ["staff", "employee", "hr", "contract"],                     "penalty": 7},
    {"policy": "data",          "keywords": ["data", "gdpr", "privacy", "information"],                  "penalty": 5},
    {"policy": "procurement",   "keywords": ["procurement", "supplier", "tender", "purchasing"],         "penalty": 9},
]

# Minimum character length for a chunk to be considered
MIN_CHUNK_LENGTH = 80

# Boost given when a query phrase appears verbatim (contiguous) in the chunk
PHRASE_BOOST = 4

# Boost per important term that appears in BOTH question AND chunk
SHARED_IMPORTANT_TERM_BOOST = 3

# Boost when a meaningful query token appears in the section title
SECTION_TITLE_BOOST = 2

# ==================================================
# UTILITIES
# ==================================================

def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tokenise(text: str) -> List[str]:
    """Lowercase word tokens, stop words removed."""
    return [w for w in re.findall(r"\b[a-z]{2,}\b", text.lower()) if w not in STOP_WORDS]


def token_set(text: str) -> Set[str]:
    return set(tokenise(text))


# ==================================================
# DOCUMENT LOADING
# ==================================================

def load_documents() -> List[Dict]:
    documents = []

    for filename in sorted(os.listdir(DOCS_PATH)):   # sorted for determinism
        if not filename.endswith(".txt"):
            continue

        # Fix: use a space not \n when deriving policy name
        policy_name = filename.replace("_", " ").replace(".txt", "").strip().title()
        path = os.path.join(DOCS_PATH, filename)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]

        current_title = "General"
        current_section: List[str] = []

        for line in lines:
            if SECTION_RE.match(line):
                if current_section:
                    text = normalise(" ".join(current_section))
                    if len(text) >= MIN_CHUNK_LENGTH:
                        documents.append({
                            "policy": policy_name,
                            "section": current_title,
                            "text": text,
                        })
                current_section = []
                current_title = line
                continue

            if META_RE.search(line):
                continue

            current_section.append(line)

        # Flush the last section
        if current_section:
            text = normalise(" ".join(current_section))
            if len(text) >= MIN_CHUNK_LENGTH:
                documents.append({
                    "policy": policy_name,
                    "section": current_title,
                    "text": text,
                })

    print(f"[load_docs] Loaded {len(documents)} section-level chunks")
    return documents


DOCUMENTS: List[Dict] = load_documents()


# ==================================================
# IDF  (computed once at load time, over all chunks)
# ==================================================

def _build_idf(docs: List[Dict]) -> Dict[str, float]:
    """
    Inverse Document Frequency: rare terms across the corpus score higher.
    idf(t) = log((N + 1) / (df(t) + 1))  — smoothed to avoid division by zero.
    """
    N = len(docs)
    df: Dict[str, int] = Counter()
    for d in docs:
        for token in token_set(d["text"]):
            df[token] += 1
    return {term: math.log((N + 1) / (count + 1)) for term, count in df.items()}


IDF: Dict[str, float] = _build_idf(DOCUMENTS)


# ==================================================
# SCORING
# ==================================================

def _score(q: str, q_tokens: Set[str], q_raw: str, doc: Dict) -> float:
    """
    Score a single document chunk against the query.

    Components:
      1. TF-IDF weighted token overlap
      2. Shared important terms boost
      3. Phrase match boost (verbatim n-gram in chunk)
      4. Section title match boost
      5. Off-topic policy penalty
    """
    text = doc["text"].lower()
    section = doc["section"].lower()
    policy = doc["policy"].lower()

    doc_tokens = token_set(doc["text"])
    overlap = q_tokens & doc_tokens

    if not overlap:
        return 0.0

    # --- 1. TF-IDF weighted overlap ---
    score = sum(IDF.get(t, 0.0) for t in overlap)

    # --- 2. Shared important terms boost ---
    for term in IMPORTANT_TERMS:
        # term must appear in BOTH the question AND the chunk
        if term in q_raw and term in text:
            score += SHARED_IMPORTANT_TERM_BOOST

    # --- 3. Phrase match boost ---
    # Check if any 2- or 3-token subsequence from the query appears verbatim in the chunk
    q_word_list = tokenise(q_raw)
    for n in (2, 3):
        for i in range(len(q_word_list) - n + 1):
            phrase = " ".join(q_word_list[i:i + n])
            if phrase in text:
                score += PHRASE_BOOST
                break   # one boost per chunk is enough

    # --- 4. Section title match ---
    for t in q_tokens:
        pattern = r"\b" + re.escape(t) + r"\b"
        if re.search(pattern, section):
            score += SECTION_TITLE_BOOST
            break   # cap at one boost

    # --- 5. Off-topic policy penalty ---
    for rule in OFF_TOPIC_PENALTIES:
        if rule["policy"] in policy:
            if not any(k in q_raw for k in rule["keywords"]):
                score -= rule["penalty"]

    return score


# ==================================================
# PUBLIC RETRIEVE FUNCTION
# ==================================================

def retrieve(question: str, max_results: int = 6) -> List[Dict]:
    """
    Return the top-scoring document chunks for the given question.

    Scoring combines:
      - TF-IDF weighted token overlap (rare shared words score higher)
      - Shared important policy terms boost
      - Verbatim phrase matching bonus
      - Section title relevance bonus
      - Off-topic policy penalties
    """
    q_raw = question.lower()
    q_tokens = token_set(question)

    if not q_tokens:
        return []

    scored = []
    for d in DOCUMENTS:
        s = _score(q_raw, q_tokens, q_raw, d)
        if s > 0:
            scored.append((s, d))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [d for _, d in scored[:max_results]]
