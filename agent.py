from typing import List, Dict


# ==================================================
# SCOPE CONTROL
# ==================================================

UNIVERSITY_KEYWORDS = [
    "arden", "university", "student", "lecturer", "teacher", "staff",
    "assessment", "exam", "attendance", "miss", "absence",
    "complaint", "complain", "appeal",
    "module", "programme", "course",
    "support", "wellbeing", "health",
    "policy", "procedure",
    "campus"
]


def is_in_scope(question: str) -> bool:
    q = question.lower()
    return any(k in q for k in UNIVERSITY_KEYWORDS)


# ==================================================
# MAIN ENTRY
# ==================================================

def generate_answer(question: str, context: List[Dict]) -> str:
    # ---- Scope gate
    if not is_in_scope(question):
        return out_of_scope_answer()

    intent = infer_intent(question)

    # ---- Safety-critical intents FIRST
    if intent == "weapon":
        return weapon_answer()

    # ---- Procedural intents
    if intent == "complaint":
        return complaint_answer()

    if intent == "staff_misconduct":
        return staff_misconduct_answer()

    if intent == "sickness":
        return sickness_answer()

    if intent == "attendance_limits":
        return attendance_limit_answer()

    # ---- General fallback
    if not context:
        return no_answer()

    return general_policy_answer(context)


# ==================================================
# INTENT DETECTION
# ==================================================

def infer_intent(question: str) -> str | None:
    q = question.lower()

    # Weapons / prohibited items (HIGH PRIORITY)
    if any(w in q for w in ["knife", "weapon", "gun", "blade", "firearm"]):
        return "weapon"

    if "complaint" in q or "complain" in q:
        return "complaint"

    if "lecturer" in q or "teacher" in q or "staff" in q:
        return "staff_misconduct"

    if "sick" in q or "ill" in q or "unwell" in q:
        return "sickness"

    if "how many days" in q or "miss" in q or "attendance" in q:
        return "attendance_limits"

    return None


# ==================================================
# SAFETY ANSWERS
# ==================================================

def weapon_answer() -> str:
    return (
        "Confidence: 85%\n\n"
        "Bringing weapons, including knives, onto University premises is not permitted.\n\n"
        "Carrying a knife or other weapon on campus may:\n"
        "- Breach University conduct and safeguarding policies\n"
        "- Trigger disciplinary action\n"
        "- Involve University security or the police, depending on circumstances\n\n"
        "If you are unsure whether an item is permitted, you should NOT bring it to campus "
        "and should seek guidance from Arden University Student Support or campus security.\n\n"
        "Source: Safeguarding Policy / Student Conduct expectations"
    )


# ==================================================
# PROCEDURAL ANSWERS
# ==================================================

def complaint_answer() -> str:
    return (
        "Confidence: 75%\n\n"
        "How to raise a complaint at Arden University:\n\n"
        "1. Attempt early informal resolution where possible (e.g. speaking with staff or Student Support).\n"
        "2. If unresolved, submit a formal complaint in writing under the Student Complaints Procedure.\n"
        "3. Complaints may relate to academic or administrative support, services, facilities, or alleged harassment or discrimination.\n\n"
        "The complaints procedure does NOT cover appeals against academic judgment or disciplinary matters.\n\n"
        "Source: Arden Student Complaints Procedure"
    )


def staff_misconduct_answer() -> str:
    return (
        "Confidence: 70%\n\n"
        "Concerns about the behaviour of a lecturer or member of staff should normally be raised "
        "through the Student Complaints Procedure.\n\n"
        "Where concerns involve harassment, discrimination, or safeguarding risks, "
        "separate safeguarding procedures may apply.\n\n"
        "Student Support can advise on the correct route."
    )


def sickness_answer() -> str:
    return (
        "Confidence: 65%\n\n"
        "If you are sick or unwell:\n\n"
        "- Inform your tutor or Student Support as soon as possible.\n"
        "- Evidence may be required depending on duration and academic impact.\n"
        "- Assessment impacts may require mitigating circumstances or extension requests.\n\n"
        "Policies do not guarantee automatic concessions.\n\n"
        "Source: Attendance and Engagement Policy"
    )


def attendance_limit_answer() -> str:
    return (
        "Confidence: 60%\n\n"
        "Arden University policies do NOT define a fixed number of days a student may miss.\n\n"
        "Attendance and engagement are assessed against expected participation, "
        "and ongoing non-engagement may trigger academic or support interventions.\n\n"
        "Requirements vary by programme and study mode.\n\n"
        "Source: Attendance and Engagement Policy"
    )


# ==================================================
# GENERAL POLICY FALLBACK
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

        lines.append(f"{c.get('policy')}")
        lines.append(f"Section: {c.get('section')}")
        lines.append(f"- {c.get('text')[:250]}...\n")

        if len(lines) >= 12:
            break

    lines.append(
        "This response is limited to published policy content and does not provide personal advice."
    )

    return "\n".join(lines)


# ==================================================
# OUT-OF-SCOPE & NO ANSWER
# ==================================================

def out_of_scope_answer() -> str:
    return (
        "Confidence: 0%\n\n"
        "This assistant can only provide information based on official Arden University policies and procedures.\n\n"
        "Your question does not relate to University regulations or student processes."
    )


def no_answer() -> str:
    return (
        "Confidence: 25%\n\n"
        "I cannot identify a specific Arden University policy that directly answers this question.\n\n"
        "You should consult your programme handbook or Student Support."
    )
