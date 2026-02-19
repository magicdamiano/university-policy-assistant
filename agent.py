# agent.py
# Final hardened policy agent with evidence-aware confidence
# Arden University–style regulatory assistant

from typing import List, Dict


MIN_CONTEXT_CHUNKS = 2


# -------------------------------------------------
# CONFIDENCE (EVIDENCE-AWARE)
# -------------------------------------------------

def calculate_confidence(context: List[Dict], question: str) -> int:
    """
    Confidence is based on:
    - number of distinct policies
    - keyword overlap between question and evidence
    - avoids false authority
    """
    if not context:
        return 25

    confidence = 30
    sources = {c["source"] for c in context}
    q_tokens = set(question.lower().split())

    # multiple policies reinforce confidence
    if len(sources) >= 2:
        confidence += 20

    # evidence overlap
    for c in context:
        text = c["text"].lower()
        overlap = sum(1 for t in q_tokens if t in text)
        confidence += min(overlap * 5, 20)

    return min(confidence, 90)


# -------------------------------------------------
# MAIN ENTRY POINT
# -------------------------------------------------

def generate_answer(question: str, context: List[Dict]) -> str:
    """
    Generate a policy-grounded answer or a safe refusal.
    """

    if len(context) < MIN_CONTEXT_CHUNKS:
        return no_answer()

    confidence = calculate_confidence(context, question)

    return f"""
Confidence: {confidence}%

Summary:
Based on official Arden University policy documents, the following guidance applies.

Policy position:
{extract_policy_position(context)}

What this means for you:
{derive_practical_guidance(context)}

Sources:
{format_sources(context)}

Important note:
This response is based solely on published Arden University policies and avoids speculation.
""".strip()


# -------------------------------------------------
# POLICY INTERPRETATION
# -------------------------------------------------

def extract_policy_position(context: List[Dict]) -> str:
    """
    Determine the regulatory stance using both filenames and content.
    """
    files = [c["source"].lower() for c in context]
    texts = [c["text"].lower() for c in context]

    if any("complaint" in f or "complaint" in t for f, t in zip(files, texts)):
        return (
            "- Arden University operates a formal complaints procedure.\n"
            "- Complaints are managed through defined procedural stages.\n"
            "- Informal resolution may be encouraged before escalation."
        )

    if any("safeguard" in f or "safety" in t for f, t in zip(files, texts)):
        return (
            "- Arden University maintains safeguarding and health & safety arrangements.\n"
            "- Incidents affecting students should be reported through appropriate channels."
        )

    if any("misconduct" in f or "discipline" in t for f, t in zip(files, texts)):
        return (
            "- Allegations of misconduct are handled under formal disciplinary procedures.\n"
            "- Investigations follow defined fairness and evidence standards."
        )

    if any("attendance" in f or "engagement" in t for f, t in zip(files, texts)):
        return (
            "- Attendance and engagement expectations are programme or module specific.\n"
            "- Persistent non-engagement may trigger academic or welfare review."
        )

    if any("exam" in t or "assessment" in t for t in texts):
        return (
            "- Assessment regulations vary by programme and module.\n"
            "- Outcomes depend on assessment rules and progression criteria."
        )

    return (
        "- Relevant regulations exist but do not prescribe a single fixed outcome.\n"
        "- Interpretation depends on context and applicable policy sections."
    )


def derive_practical_guidance(context: List[Dict]) -> str:
    """
    Convert policy stance into practical, safe guidance.
    """
    files = [c["source"].lower() for c in context]
    texts = [c["text"].lower() for c in context]

    if any("complaint" in f or "complaint" in t for f, t in zip(files, texts)):
        return (
            "- Clearly identify the issue you wish to raise.\n"
            "- Review deadlines and evidence requirements in the complaints policy.\n"
            "- Submit your complaint via the official Arden University process."
        )

    if any("safeguard" in f or "safety" in t for f, t in zip(files, texts)):
        return (
            "- Seek immediate assistance if there is a safety concern.\n"
            "- Report incidents to University staff or student support services.\n"
            "- Follow safeguarding or health & safety guidance."
        )

    if any("misconduct" in f or "discipline" in t for f, t in zip(files, texts)):
        return (
            "- Report concerns using the appropriate University reporting route.\n"
            "- Avoid direct confrontation if there is risk.\n"
            "- Allow the University to manage the matter formally."
        )

    if any("attendance" in f or "engagement" in t for f, t in zip(files, texts)):
        return (
            "- Review your programme or module attendance requirements.\n"
            "- Notify the University if absences are unavoidable.\n"
            "- Engage with student support services if issues persist."
        )

    if any("exam" in t or "assessment" in t for t in texts):
        return (
            "- Review assessment regulations in your programme handbook.\n"
            "- Check eligibility for reassessment or resits.\n"
            "- Contact your programme team for academic advice."
        )

    return (
        "- Review the relevant policy document carefully.\n"
        "- Contact your programme team or student support services for clarification."
    )


# -------------------------------------------------
# SOURCE FORMATTING
# -------------------------------------------------

def format_sources(context: List[Dict]) -> str:
    """
    Group evidence by policy with metadata and optional PDF links.
    """
    grouped = {}

    for c in context:
        meta = c.get("meta", {})
        key = (
            meta.get("policy_title", c["source"]),
            meta.get("policy_code", "Not specified"),
            meta.get("effective_date", "Not specified"),
            meta.get("pdf_link")
        )
        grouped.setdefault(key, []).append(c["text"].strip())

    output = []

    for (title, code, year, link), texts in grouped.items():
        header = f"{title} (Code: {code}, Effective: {year})"
        if link:
            header += f"\nDownload: {link}"

        output.append(header)
        for t in texts[:3]:
            output.append(f"- {t}")
        output.append("")

    return "\n".join(output)


# -------------------------------------------------
# SAFE REFUSAL
# -------------------------------------------------

def no_answer() -> str:
    return """
Confidence: 25%

I cannot identify an Arden University regulation that directly answers this question
based on the official documents currently available.

This may be because:
- The question is too general, or
- The relevant policy is programme-specific, or
- No explicit regulation exists at university level.

Recommended next steps:
- Review your programme or module handbook
- Consult the relevant official policy document
- Contact Arden University student support services

This response avoids speculation and is limited to confirmed policy content.
""".strip()
