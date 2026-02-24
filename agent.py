import re
from typing import List, Dict

# ==================================================
# DOMAIN & INTENT CONSTANTS
# ==================================================

DOMAIN_KEYWORDS = {
    # Core academic lifecycle
    "study", "studying", "student", "programme", "program", "course", "module",
    "degree", "undergraduate", "postgraduate", "masters", "dissertation",

    # Assessment & exams
    "assessment", "exam", "examination", "test", "quiz", "assignment",
    "coursework", "submission", "resubmission", "resit", "retake",
    "grade", "mark", "marking", "feedback", "results", "pass", "fail",

    # Appeals, complaints, procedures
    "appeal", "appeals", "complaint", "complaints", "procedure", "process",
    "policy", "regulation", "regulations", "academic judgement",
    "procedural irregularity",

    # Attendance & engagement
    "attendance", "engagement", "engaging", "non-attendance",
    "participation", "miss", "absence", "absent",

    # Integrity & conduct
    "plagiarism", "plagiarise", "cheating", "collusion",
    "misconduct", "academic integrity", "disciplinary",

    # Mitigation & support
    "extension", "extensions", "deadline", "deadlines",
    "mitigating", "mitigation", "extenuating", "circumstances",
    "illness", "medical", "evidence",

    # Progression & status
    "progression", "progress", "repeat", "termination",
    "withdraw", "withdrawal", "suspension", "interruption",
    "deferral", "defer",

    # Support & wellbeing
    "support", "wellbeing", "mental health", "disability",
    "reasonable adjustments", "inclusion",

    # Institutional
    "university", "arden", "campus", "tutor", "academic board",
    "registry", "student support"
}

ATTENDANCE_ALIASES = {
    "attendance", "engagement", "engaging", "attend", "attending",
    "attended", "miss classes", "miss lectures", "miss sessions",
    "skip classes", "skip lectures",
    "not attending", "not engaging", "stop engaging",
    "poor attendance", "low attendance",
    "absence", "absent", "non attendance", "non-attendance",
    "stopped attending", "haven't attended", "stop going to class",
    "stop going to classes", "what happens if i don't attend",
    "what if i stop engaging", "stop attending"
}

PLAGIARISM_POLICIES = {
    "academic integrity",
    "misconduct",
    "academic misconduct",
    "cheating",
    "collusion",
    "plagiarism"
}

SUPPORT_INTENT_KEYWORDS = {
    "stress", "stressed", "anxious", "anxiety",
    "overwhelmed", "worried", "panic",
    "mental health", "pressure", "burnout"
}

APPEAL_ALIASES = {
    "appeal", "appeals", "academic appeal",
    "appeal decision", "appeal judgement",
    "appeal mark", "appeal grade", "appeal result"
}

EXTENUATING_ALIASES = {
    # --- Illness & health ---
    "ill", "sick", "unwell", "medical", "health issue",
    "hospital", "hospitalised", "hospitalized",
    "surgery", "operation", "injured", "injury",
    "covid", "flu", "virus",

    # --- Mental health ---
    "stress", "stressed", "anxiety", "anxious",
    "depression", "depressed",
    "mental health", "panic", "panic attack",
    "burnout", "overwhelmed",

    # --- Family & personal emergencies ---
    "family emergency", "personal emergency",
    "personal circumstances", "personal issues",
    "issues at home", "family issues",
    "bereavement", "funeral", "death in family",
    "parent ill", "relative ill",

    # --- Accidents & unexpected events ---
    "accident", "emergency", "unexpected situation",
    "car accident", "injured myself",

    # --- Impact on study (very important signals) ---
    "missed deadline", "missed exam",
    "could not submit", "couldn't submit",
    "could not attend", "couldn't attend",
    "unable to submit", "unable to attend",
    "failed because", "affected my assessment",
    "affected my exam", "affected my coursework"
}

WITHDRAWAL_ALIASES = {
    "withdraw", "withdrawal", "leave course",
    "quit course", "drop out",
    "suspend studies", "interruption",
    "defer", "deferral"
}

MAX_POLICIES = 2


# ==================================================
# FIXED ANSWERS
# ==================================================

def attendance_limit_answer() -> str:
    return (
        "Confidence: 60%\n\n"
        "Arden University does not define a fixed number of classes you may miss.\n\n"
        "Attendance and engagement are assessed based on expected participation. "
        "Ongoing non-engagement may trigger academic monitoring, support "
        "interventions, or withdrawal procedures depending on your programme "
        "and study mode.\n\n"
        "If you are unwell or facing difficulties, you should inform your tutor "
        "or Student Support as soon as possible.\n\n"
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
        key = (c["policy"], c["section"])
        if key in seen:
            continue

        seen.add(key)

        sentences = re.split(r"(?<=[.!?])\s+", c["text"])
        snippet = sentences[0]

        lines.append(f"{c['policy']}")
        lines.append(f"Section: {c['section']}")
        lines.append(f"- {snippet}\n")

        if len(seen) >= MAX_POLICIES:
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
        "I can only help with questions about Arden University regulations, "
        "policies, and student processes.\n\n"
        "For example, I can help with attendance rules, appeals, assessments, "
        "academic integrity, extensions, or withdrawals.\n\n"
        "Your question does not fall within that scope."
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

def is_domain_question(question: str) -> bool:
    q = question.lower()

    # Core academic / regulatory terms
    if any(k in q for k in DOMAIN_KEYWORDS):
        return True

    # Attendance & engagement should count as domain
    if any(a in q for a in ATTENDANCE_ALIASES):
        return True

    # Appeals phrasing (sometimes no "policy" words)
    if any(a in q for a in APPEAL_ALIASES):
        return True

    return False

def is_support_question(question: str) -> bool:
    q = question.lower()
    return any(k in q for k in SUPPORT_INTENT_KEYWORDS)

def answer(question: str, context: List[Dict]) -> str:
    q = question.lower()

    # 1. Support / wellbeing intent (handled BEFORE domain gate)
    if is_support_question(q):
        return (
            "Confidence: 40%\n\n"
            "I can’t provide personal or wellbeing advice.\n\n"
            "However, Arden University policies reference support mechanisms such as "
            "reasonable adjustments, extensions, mitigating circumstances, and "
            "Student Support services.\n\n"
            "If stress or anxiety is affecting your studies, you may wish to contact "
            "Student Support or review guidance on mitigating or extenuating circumstances."
        )

    # 2. Hard domain gate
    if not is_domain_question(q):
        return out_of_scope_answer()

    # 3. Attendance (strong intent)
    if any(a in q for a in ATTENDANCE_ALIASES):
        return attendance_limit_answer()

    # 4. Academic appeals
    if any(a in q for a in APPEAL_ALIASES):
        return academic_appeal_answer(context)

    # 5. Plagiarism / misconduct (filter context)
    if "plagiarism" in q or "misconduct" in q:
        filtered = [
            c for c in context
            if any(p in c["policy"].lower() for p in PLAGIARISM_POLICIES)
        ]
        if filtered:
            return general_policy_answer(filtered)
        return no_answer()

    # 6. Withdrawal / interruption
    if any(a in q for a in WITHDRAWAL_ALIASES):
        if context:
            return general_policy_answer(context)
        return no_answer()

    # 7. Generic policy fallback
    if context:
        return general_policy_answer(context)

    return no_answer()

# ==================================================
# BACKWARDS COMPATIBILITY
# ==================================================
# app.py imports generate_answer — DO NOT REMOVE

def generate_answer(question: str, context: List[Dict]) -> str:
    return answer(question, context)
