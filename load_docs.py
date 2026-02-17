import os

DOCS_DIR = "docs"

def load_documents():
    chunks = []

    for filename in os.listdir(DOCS_DIR):
        path = os.path.join(DOCS_DIR, filename)
        if not os.path.isfile(path):
            continue

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        parts = text.split("SECTION:")
        header = parts[0]

        for part in parts[1:]:
            lines = part.strip().splitlines()
            section_title = lines[0].strip()
            section_body = "\n".join(lines[1:]).strip()

            chunks.append({
                "document": filename,
                "section": section_title,
                "text": section_body
            })

    return chunks


if __name__ == "__main__":
    for c in load_documents():
        print(c)
