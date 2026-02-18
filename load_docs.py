import os

DOCS_DIR = "docs"

def load_docs():
    docs = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(DOCS_DIR, filename), "r", encoding="utf-8", errors="ignore") as f:
                docs.append(f.read())
    print(f"[load_docs] Loaded {len(docs)} documents")
    return docs
