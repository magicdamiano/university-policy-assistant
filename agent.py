import re
from typing import List, Dict

# ==================================================
# INTENT KEYWORDS
# ==================================================

ATTENDANCE_ALIASES = [
    "attendance",
    "miss",
    "absent",
    "classes",
    "sessions",
    "lectures"
]

IMPORTANT_TERMS = [
    "must",
    "required",
    "will",
    "may",
    "cannot",
    "deadline",
    "appeal",
    "misconduct",
    "penalty",
    "withdrawal"
]

# ==================================================
# SPECIFIC ANSWERS
# ==================================================

def attendance_limit_answer() -> str:
    return (
        "Confidence: 60%\n\n"
        "Arden University does not define a fixed number of classes you may miss.\n\n"
        "Attendance and engagement are assessed based on expected participation. "
        "Ongoing non-engagement may trigger academic monitoring, support interventions, "
        "or withdrawal procedures depending on your programme and study mode.\n\n"
        "If you are unwell or facing difficulties, you should inform your tutor or "
        "Student Support as soon as possible.\n\n"
        "Source: Attendance and Engagement Policy"
    )


def academic_appeal_answer(context: List[Dict]) -> str:
    return (
        "Confidence: 70%\n\n"
        "You cannot normally appeal academic judgement itself.\n\n"
        "However, you may submit an academic appeal if you believe:\n"
        "- A procedural irregularity occurred\n"
        "- Relevant evidence was not considered\n"
        "- Approved mitigating circumstances affected the assessment\n\n"
        "Appeals must follow the Academic Appeals Procedure and be submitted "
        "within the published timescales.\n\n"
        "Source: Academic Appeals Process"
    )


# ==================================================
# GENERIC POLICY ANSWER
# ==================================================

def general_policy_answer(context: List[Dict]) -> str:
    lines = [
        "Confidence: 50%\n",
        "Based on official Arden University policy documents:\n"
    ]

    seen = set()

    for c in context:
        key = (c.get("policy"), c.get("section"))
        if key in seen:
            continue
        seen.add(key)

        # Take only the first clean sentence
        sentences = re.split(r"(?<=[.!?])\s+", c["text"])
        snippet = sentences[0]

        lines.append(f"{c['policy']}")
        lines.append(f"Section: {c['section']}")
        lines.append(f"- {snippet}\n")

        if len(lines) >= 12:
            break

    lines.append(
        "This response is limited to published policy content and does not provide personal advice."
    )

    return "\n".join(lines)


# ==================================================
# FALLBACK ANSWERS
# ==================================================

def out_of_scope_answer() -> str:
    return (
        "Confidence: 0%\n\n"
        "This assistant can only provide information based on official "
        "Arden University policies and procedures.\n\n"
        "Your question does not relate to University regulations or student processes."
    )


def no_answer() -> str:
    return (
        "Confidence: 25%\n\n"
        "I cannot identify a specific Arden University policy that directly answers this question.\n\n"
        "You should consult your programme handbook or Student Support."
    )


# ==================================================
# MAIN ROUTER
# ==================================================

def answer(question: str, context: List[Dict]) -> str:
    q = question.lower()

    if any(a in q for a in ATTENDANCE_ALIASES):
        return attendance_limit_answer()

    if "appeal" in q and "academic" in q:
        return academic_appeal_answer(context)

    if context:
        return general_policy_answer(context)

    return out_of_scope_answer()


# ==================================================
# BACKWARDS COMPATIBILITY
# ==================================================
# app.py imports generate_answer — do NOT remove this

def generate_answer(question: str, context: List[Dict]) -> str:
    return answer(question, context)
