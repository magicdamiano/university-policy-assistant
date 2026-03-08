import re
from typing import List, Dict

# ==================================================
# DOMAIN & INTENT CONSTANTS
# ==================================================

DOMAIN_KEYWORDS = {
    # Core academic lifecycle
    "study", "studying", "student", "programme",
    "program", "course", "module",
    "degree", "undergraduate", "postgraduate",
    "masters", "dissertation",
    # Assessment & exams
    "assessment", "exam", "examination", "test",
    "quiz", "assignment",
    "coursework", "submission", "resubmission",
    "resit", "retake",
    "grade", "mark", "marking", "feedback",
    "results", "pass", "fail",
    # Appeals, complaints, procedures
    "appeal", "appeals", "complaint", "complaints",
    "procedure", "process",
    "policy", "regulation", "regulations",
    # Attendance & engagement
    "attendance", "engagement", "engaging",
    "non-attendance", "participation",
    "absence", "absent",
    # Integrity & conduct
    "plagiarism", "plagiarise", "cheating",
    "collusion", "misconduct", "disciplinary",
    # Mitigation & support
    "extension", "extensions", "deadline", "deadlines",
    "mitigating", "mitigation", "extenuating",
    "circumstances", "illness", "medical", "evidence",
    # Progression & status
    "progression", "progress", "repeat", "termination",
    "withdraw", "withdrawal", "suspension", "interruption",
    "deferral", "defer",
    # Support & wellbeing
    "support", "wellbeing", "disability",
    "reasonable adjustments", "inclusion",
    # Institutional
    "university", "arden", "campus", "tutor",
    "registry", "student support"
}

ATTENDANCE_ALIASES = {
    "attendance", "engagement", "engaging",
    "attend", "attending", "attended",
    "absence", "absent", "non attendance", "non-attendance",
    "poor attendance", "low attendance",
}

ATTENDANCE_PHRASE_PATTERNS = [
    r"\bmiss(?:ing|ed)?\s+(?:class(?:es)?|lecture[s]?|session[s]?|seminar[s]?)\b",
    r"\bhow\s+many\s+(?:class(?:es)?|lecture[s]?|session[s]?)\s+can\s+i\s+miss\b",
    r"\bskip(?:ped|ping)?\s+(?:class(?:es)?|lecture[s]?|session[s]?)\b",
    r"\bnot\s+(?:attending|engaging|going\s+to\s+class(?:es)?)\b",
    r"\bstopped?\s+attending\b",
    r"\bhaven'?t\s+attended\b",
    r"\bwhat\s+(?:if|happens)\s+(?:i\s+)?(?:don'?t|stop)\s+(?:attend|engag)\w*\b",
    r"\bstop\s+going\s+to\s+class(?:es)?\b",
    r"\bcan\s+i\s+miss\s+(?:class(?:es)?|lecture[s]?|session[s]?)\b",
]

PLAGIARISM_POLICIES = {
    "academic integrity",
    "misconduct",
    "academic misconduct",
    "cheating",
    "collusion",
    "plagiarism",
}

SUPPORT_INTENT_KEYWORDS = {
    "stressed", "anxious", "anxiety",
    "overwhelmed", "worried", "panicking",
    "mental health", "burnout",
}

SUPPORT_WITH_POLICY_PATTERNS = [
    r"\b(?:stressed?|anxious|overwhelmed|worried|panic)\b.*\b(?:exam|deadline|submission|coursework|assignment|appeal|grade|fail)\b",
    r"\b(?:exam|deadline|submission|coursework)\b.*\b(?:stressed?|anxious|overwhelmed|worried)\b",
]

APPEAL_ALIASES = {
    "appeal", "appeals", "academic appeal",
    "appeal decision", "appeal judgement",
    "appeal mark", "appeal grade", "appeal result",
}

APPEAL_PHRASE_PATTERNS = [
    r"\bappeal(?:ing|ed)?\s+(?:my\s+)?(?:mark|grade|result|decision|assessment)\b",
    r"\bcan\s+i\s+appeal\b",
    r"\bhow\s+(?:do\s+i|to)\s+(?:submit\s+an?\s+)?appeal\b",
]

EXTENUATING_ALIASES = {
    # Illness & health
    "ill", "sick", "unwell", "medical", "health issue",
    "hospital", "hospitalised", "hospitalized",
    "surgery", "operation", "injured", "injury",
    "covid", "flu", "virus",
    # Mental health
    "depression", "depressed", "panic attack",
    # Family & personal emergencies
    "family emergency", "personal emergency",
    "personal circumstances", "personal issues",
    "issues at home", "family issues",
    "bereavement", "funeral", "death in family",
    "parent ill", "relative ill",
    # Accidents & unexpected events
    "accident", "emergency", "unexpected situation",
    "car accident", "injured myself",
    # Impact on study
    "missed deadline", "missed exam",
    "could not submit", "couldn't submit",
    "could not attend", "couldn't attend",
    "unable to submit", "unable to attend",
    "failed because", "affected my assessment",
    "affected my exam", "affected my coursework",
}

EXTENUATING_PHRASE_PATTERNS = [
    r"\b(?:missed?|couldn'?t|could not|unable to)\s+(?:submit|attend|complete)\b",
    r"\b(?:ill|sick|injured|hospitalised?|hospitalized)\b.*\b(?:exam|assessment|deadline|coursework)\b",
    r"\b(?:bereavement|family emergency|personal emergency)\b",
    r"\b(?:extension|extenuating|mitigating)\s+(?:request|circumstances?|evidence)\b",
]

WITHDRAWAL_ALIASES = {
    "withdraw", "withdrawal", "leave course",
    "quit course", "drop out", "dropping out",
    "dropped out", "dropout",
    "suspend studies", "interruption",
    "defer", "deferral",
}

MAX_POLICIES = 5  # Increased from 2 to 5 — use more retrieved context


# ==================================================
# OFF-TOPIC BLOCKLIST
# ==================================================

OFF_TOPIC_SUBJECTS = {
    # Weapons & safety threats
    "knife", "knives", "weapon", "weapons", "gun", "guns", "firearm",
    "bomb", "explosive", "blade", "sword", "axe", "violence",
    # Food & drink
    "cook", "cooking", "recipe", "food", "eat", "eating", "drink",
    "coffee", "lunch", "dinner", "breakfast", "meal", "pasta", "pizza",
    # Transport & travel (non-academic)
    "drive", "driving", "car", "bus", "train", "flight", "travel",
    "parking", "commute",
    # Weather & environment
    "weather", "rain", "sunny", "temperature", "forecast",
    # Entertainment
    "movie", "film", "song", "music", "game", "sport", "football",
    "netflix", "spotify",
    # General life / personal
    "relationship", "dating", "boyfriend", "girlfriend", "marriage",
    "shopping", "fashion", "hair", "makeup",
}


# ==================================================
# MATCHING HELPERS
# ==================================================

def _token_match(q: str, aliases: set) -> bool:
    for alias in aliases:
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, q):
            return True
    return False


def _phrase_match(q: str, patterns: List[str]) -> bool:
    return any(re.search(p, q) for p in patterns)


def _confidence_from_scores(scores: List[float], base: int = 50) -> int:
    """
    Derive confidence from actual retrieval scores rather than chunk count.
    Higher top scores and tighter clustering = more confidence.
    Returns an integer 0-95.
    """
    if not scores:
        return max(0, base - 20)

    top = scores[0]
    # Normalise: a score of ~20 is strong, ~5 is weak
    score_boost = min(int(top * 1.5), 30)

    # Tight clustering between top scores adds a little more confidence
    if len(scores) >= 2:
        gap = top - scores[1]
        if gap < 2:  # top result isn't clearly dominant
            score_boost = max(0, score_boost - 5)

    return min(95, base + score_boost)


# ==================================================
# CONTEXT SYNTHESIS
# ==================================================

def _synthesise_context(context: List[Dict]) -> str:
    """
    Build a readable multi-chunk answer body from retrieved policy sections.
    Groups by policy to avoid repetition and shows meaningful excerpts.
    """
    seen_keys = set()
    grouped: Dict[str, List[Dict]] = {}

    for c in context:
        key = (c["policy"], c["section"])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        grouped.setdefault(c["policy"], []).append(c)
        if len(seen_keys) >= MAX_POLICIES:
            break

    lines = []
    for policy, chunks in grouped.items():
        for chunk in chunks:
            # Use up to 3 sentences from each chunk for a richer answer
            sentences = re.split(r'(?<=[.!?])\s+', chunk["text"])
            excerpt = " ".join(sentences[:3]).strip()
            if excerpt:
                lines.append(f"**{chunk['policy']} — {chunk['section']}**")
                lines.append(excerpt)
                lines.append("")

    return "\n".join(lines).strip()


# ==================================================
# FIXED ANSWERS
# ==================================================

def attendance_limit_answer() -> str:
    return (
        "Arden University does not define a fixed number of classes you may miss.\n\n"
        "Attendance and engagement are assessed based on expected participation. "
        "Ongoing non-engagement may trigger academic monitoring, support "
        "interventions, or withdrawal procedures depending on your programme "
        "and study mode.\n\n"
        "If you are unwell or facing difficulties, you should inform your tutor "
        "or Student Support as soon as possible.\n\n"
        "Source: Attendance and Engagement Policy"
    ), 60


def academic_appeal_answer(context: List[Dict], scores: List[float]) -> tuple:
    confidence = _confidence_from_scores(scores, base=65)
    body = (
        "You cannot normally appeal academic judgement itself.\n\n"
        "However, you may submit an academic appeal if you believe:\n"
        "- A procedural irregularity occurred\n"
        "- Relevant evidence was not considered\n"
        "- Approved mitigating circumstances affected the assessment\n\n"
        "Appeals must follow the Academic Appeals Procedure and be submitted "
        "within the published timescales."
    )
    if context:
        extra = _synthesise_context(context)
        if extra:
            body += f"\n\n{extra}"
    body += "\n\nSource: Academic Appeals Process"
    return body, confidence


def extenuating_circumstances_answer(context: List[Dict], scores: List[float]) -> tuple:
    confidence = _confidence_from_scores(scores, base=60)
    if context:
        body = (
            "If personal circumstances have affected your ability to study or complete "
            "assessments, you may be eligible to submit an Extenuating Circumstances claim.\n\n"
        )
        body += _synthesise_context(context)
        return body, confidence
    body = (
        "If personal circumstances have affected your ability to study or complete "
        "assessments, you may be eligible to submit an Extenuating Circumstances claim.\n\n"
        "You should:\n"
        "- Notify your tutor or Student Support as soon as possible\n"
        "- Gather supporting evidence (e.g. medical documentation)\n"
        "- Submit your claim within the published deadline\n\n"
        "Source: Extenuating Circumstances Policy"
    )
    return body, confidence


# ==================================================
# GENERIC POLICY ANSWER
# ==================================================

def general_policy_answer(
    context: List[Dict],
    scores: List[float],
    label: str = "Based on official Arden University policy documents",
    base_confidence: int = 50
) -> tuple:
    confidence = _confidence_from_scores(scores, base=base_confidence)
    body_parts = [f"{label}:\n"]
    body_parts.append(_synthesise_context(context))
    body_parts.append(
        "\nThis response is limited to published policy content and does not provide personal advice."
    )
    return "\n".join(body_parts), confidence


# ==================================================
# FALLBACK ANSWERS
# ==================================================

def out_of_scope_answer() -> tuple:
    return (
        "I can only help with questions about Arden University regulations, "
        "policies, and student processes.\n\n"
        "For example, I can help with attendance rules, appeals, assessments, "
        "academic integrity, extensions, or withdrawals.\n\n"
        "Your question does not fall within that scope."
    ), 0


def no_answer() -> tuple:
    return (
        "I cannot identify a specific Arden University policy that directly answers this question.\n\n"
        "You should consult your programme handbook or Student Support."
    ), 25


# ==================================================
# INTENT DETECTORS
# ==================================================

def is_domain_question(question: str) -> bool:
    q = question.lower()
    if _token_match(q, OFF_TOPIC_SUBJECTS):
        return False
    if _token_match(q, DOMAIN_KEYWORDS):
        return True
    if is_attendance_question(q):
        return True
    if is_appeal_question(q):
        return True
    if is_extenuating_question(q):
        return True
    if is_withdrawal_question(q):
        return True
    return False


def is_attendance_question(q: str) -> bool:
    return _token_match(q, ATTENDANCE_ALIASES) or _phrase_match(q, ATTENDANCE_PHRASE_PATTERNS)


def is_appeal_question(q: str) -> bool:
    return _token_match(q, APPEAL_ALIASES) or _phrase_match(q, APPEAL_PHRASE_PATTERNS)


def is_extenuating_question(q: str) -> bool:
    return _token_match(q, EXTENUATING_ALIASES) or _phrase_match(q, EXTENUATING_PHRASE_PATTERNS)


def is_support_question(q: str) -> bool:
    """
    Only fires if the user is expressing distress WITHOUT a clear policy context.
    If they mention stress AND a policy topic, route to policy instead.
    """
    has_support_signal = _token_match(q, SUPPORT_INTENT_KEYWORDS)
    if not has_support_signal:
        return False
    if _phrase_match(q, SUPPORT_WITH_POLICY_PATTERNS):
        return False
    return True


def is_plagiarism_question(q: str) -> bool:
    return _token_match(q, {"plagiarism", "plagiarise", "misconduct", "collusion", "cheating", "academic integrity"})


def is_withdrawal_question(q: str) -> bool:
    return _token_match(q, WITHDRAWAL_ALIASES)


# ==================================================
# MAIN ROUTER
# ==================================================

def answer(question: str, context: List[Dict], scores: List[float] = None) -> str:
    """
    Route the question to the best answer strategy.
    `scores` should be the retrieval scores corresponding to each context chunk
    (in the same order). If not provided, confidence falls back to chunk count.
    """
    q = question.lower()
    scores = scores or []

    # 1. Support / wellbeing intent ONLY when no policy topic is mixed in
    if is_support_question(q):
        body = (
            "I can't provide personal or wellbeing advice.\n\n"
            "However, Arden University policies reference support mechanisms such as "
            "reasonable adjustments, extensions, mitigating circumstances, and "
            "Student Support services.\n\n"
            "If stress or anxiety is affecting your studies, you may wish to contact "
            "Student Support or review guidance on mitigating or extenuating circumstances."
        )
        return _format_response(body, 40)

    # 2. Hard domain gate
    if not is_domain_question(q):
        body, confidence = out_of_scope_answer()
        return _format_response(body, confidence)

    # 3. Extenuating / mitigating circumstances
    if is_extenuating_question(q):
        filtered = [
            c for c in context
            if "misconduct" not in c["policy"].lower()
            and "integrity" not in c["policy"].lower()
            and "disability" not in c["policy"].lower()
            and "reasonable adjustments" not in c["policy"].lower()
            and "attendance" not in c["policy"].lower()
        ]
        filtered_scores = [scores[i] for i, c in enumerate(context)
            if "misconduct" not in context[i]["policy"].lower()
            and "integrity" not in context[i]["policy"].lower()
            and "disability" not in context[i]["policy"].lower()
            and "reasonable adjustments" not in context[i]["policy"].lower()
            and "attendance" not in context[i]["policy"].lower()
        ] if scores else []
        body, confidence = extenuating_circumstances_answer(filtered or context, filtered_scores or scores)
        return _format_response(body, confidence)

    # 4. Attendance (strong intent — fixed answer)
    if is_attendance_question(q):
        body, confidence = attendance_limit_answer()
        return _format_response(body, confidence)

    # 5. Academic appeals
    if is_appeal_question(q):
        filtered = [
            c for c in context
            if "misconduct" not in c["policy"].lower()
            and "integrity" not in c["policy"].lower()
            and "withdrawal" not in c["policy"].lower()
            and "extenuating" not in c["policy"].lower()
            and "attendance" not in c["policy"].lower()
        ]
        filtered_scores = [scores[i] for i, c in enumerate(context)
            if "misconduct" not in context[i]["policy"].lower()
            and "integrity" not in context[i]["policy"].lower()
            and "withdrawal" not in context[i]["policy"].lower()
            and "extenuating" not in context[i]["policy"].lower()
            and "attendance" not in context[i]["policy"].lower()
        ] if scores else []
        body, confidence = academic_appeal_answer(filtered or context, filtered_scores or scores)
        return _format_response(body, confidence)

    # 6. Plagiarism / misconduct (filter context to relevant policies)
    if is_plagiarism_question(q):
        filtered = [
            c for c in context
            if any(p in c["policy"].lower() for p in PLAGIARISM_POLICIES)
        ]
        filtered_scores = [scores[i] for i, c in enumerate(context) if any(p in c["policy"].lower() for p in PLAGIARISM_POLICIES)] if scores else []
        if filtered:
            body, confidence = general_policy_answer(filtered, filtered_scores, base_confidence=55)
            return _format_response(body, confidence)
        body, confidence = no_answer()
        return _format_response(body, confidence)

    # 7. Withdrawal / interruption
    if is_withdrawal_question(q):
        if context:
            body, confidence = general_policy_answer(context, scores, base_confidence=55)
            return _format_response(body, confidence)
        body, confidence = no_answer()
        return _format_response(body, confidence)

    # 8. Generic policy fallback
    if context:
        body, confidence = general_policy_answer(context, scores)
        return _format_response(body, confidence)

    body, confidence = no_answer()
    return _format_response(body, confidence)


def _format_response(body: str, confidence: int) -> str:
    """Prepend the confidence line that app.py expects to parse."""
    return f"Confidence: {confidence}%\n\n{body}"


# ==================================================
# BACKWARDS COMPATIBILITY
# ==================================================

# app.py imports generate_answer — DO NOT REMOVE
def generate_answer(question: str, context: List[Dict]) -> str:
    return answer(question, context)
