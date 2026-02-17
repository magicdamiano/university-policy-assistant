import os
import re

DOCS_DIR = "docs"

# Patterns to remove (safe cleanup)
CLEAN_PATTERNS = [
    r":contentReference\\[[^\\]]+\\]\\{[^\\}]+\\}",
    r":contentReference\\[[^\\]]+\\]",
]

def clean_text(text):
    for pattern in CLEAN_PATTERNS:
        text = re.sub(pattern, "", text)
    # Normalize excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"

def main():
    for filename in os.listdir(DOCS_DIR):
        path = os.path.join(DOCS_DIR, filename)
        if not os.path.isfile(path):
            continue

        with open(path, "r", encoding="utf-8") as f:
            original = f.read()

        cleaned = clean_text(original)

        with open(path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"Cleaned: {filename}")

if __name__ == "__main__":
    main()
