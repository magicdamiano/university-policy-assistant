import os

DOCS_DIR = "docs"

def load_documents():
    chunks = []
    doc_id = 0

    if not os.path.isdir(DOCS_DIR):
        print("[load_docs] docs/ folder not found")
        return chunks

    for filename in os.listdir(DOCS_DIR):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(DOCS_DIR, filename)

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                doc_id += 1
                chunks.append({
                    "id": doc_id,
                    "source": filename,
                    "text": line
                })

    print(f"[load_docs] Loaded {len(chunks)} lines")
    return chunks
