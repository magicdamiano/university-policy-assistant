from load_docs import load_documents

print("Loading documents...")
DOCUMENT_CHUNKS = load_documents()
print(f"Loaded {len(DOCUMENT_CHUNKS)} document chunks.")

def normalize(text):
    return text.lower()

def retrieve(question, top_k=3):
    q_words = set(normalize(question).split())
    scored = []

    for c in DOCUMENT_CHUNKS:
        text_words = set(normalize(c["text"]).split())
        overlap = len(q_words & text_words)
        if overlap > 0:
            scored.append((overlap, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]
