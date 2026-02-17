RAW_FILE = "raw_policies/arden_regulatory_framework_v9_raw.txt"
OUTPUT_FILE = "docs/arden_regulatory_framework_focused.txt"

SECTIONS = {
    "Assessment Regulations": [
        "assessment",
        "submission",
        "examination",
        "marking",
        "reassessment",
        "extension",
        "deadline"
    ],
    "Progression Rules": [
        "progression",
        "completion",
        "credit",
        "level",
        "withdrawal",
        "fail"
    ],
    "Award Classification": [
        "award",
        "classification",
        "degree",
        "masters",
        "bachelor"
    ],
    "Governance and Authority": [
        "academic board",
        "governance",
        "regulatory framework",
        "authority"
    ]
}

def extract_sections(text):
    blocks = text.split("\n\n")
    extracted = {section: [] for section in SECTIONS}

    for block in blocks:
        block_lower = block.lower()
        for section, keywords in SECTIONS.items():
            if any(keyword in block_lower for keyword in keywords):
                extracted[section].append(block.strip())
    return extracted


def main():
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    extracted = extract_sections(text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("Document: Arden University Regulatory Framework v9 (Focused)\n")
        f.write("Institution: Arden University\n")
        f.write("Document Type: Academic Regulations\n\n")

        for section, blocks in extracted.items():
            if not blocks:
                continue

            f.write(f"SECTION: {section}\n")
            for block in blocks:
                f.write(block + "\n\n")

        f.write("END OF DOCUMENT\n")

    print(f"Focused regulatory framework written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
