from load_docs import load_documents

DOCUMENTS = load_documents()

def normalize(text):
    return text.lower()

def retrieve(question, top_k=5):
    q_words = set(normalize(question).split())
    scored = []

    for d in DOCUMENTS:
        text_words = set(normalize(d["text"]).split())
        overlap = len(q_words & text_words)
        if overlap > 0:
            scored.append((overlap, d))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:top_k]]
