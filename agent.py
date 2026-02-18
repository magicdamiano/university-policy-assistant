def detect_topic(question):
    q = question.lower()

    if any(w in q for w in [
        "complaint", "complain", "unhappy", "not happy", "grievance",
        "appeal", "problem"
    ]):
        return "complaints"

    if any(w in q for w in [
        "attendance", "attend", "miss", "absence", "absent",
        "engagement", "days"
    ]):
        return "attendance"

    if any(w in q for w in [
        "injured", "injury", "hurt", "accident",
        "safety", "incident", "harm"
    ]):
        return "safeguarding"

    if any(w in q for w in [
        "misconduct", "misbehave", "discipline",
        "behaviour", "lecturer", "staff"
    ]):
        return "misconduct"

    return "unknown"


def ask_agent(question, sources):
    topic = detect_topic(question)

    # LOW CONFIDENCE
    if not sources or topic == "unknown":
        return {
            "confidence": "25%",
            "answer": (
                "I cannot identify an Arden University regulation that directly answers "
                "this question based on the official documents currently available.\n\n"
                "University requirements often vary by programme or service area. You should consult:\n"
                "- Your programme or module handbook\n"
                "- The relevant official policy document\n"
                "- Arden University student support services\n\n"
                "This response avoids speculation and is limited to confirmed policy content."
            )
        }

    # ATTENDANCE
    if topic == "attendance":
        return {
            "confidence": "90%",
            "answer": (
                "Summary:\n"
                "Arden University regulations do not define a fixed number of days that a student may miss. "
                "Attendance and engagement expectations are typically defined at programme or module level.\n\n"
                "Regulatory position:\n"
                "- Attendance rules are programme-specific.\n"
                "- Engagement may be monitored rather than measured strictly by days absent.\n"
                "- Persistent non-engagement may trigger academic or welfare review.\n\n"
                "Recommended next steps:\n"
                "- Review your programme or module handbook.\n"
                "- Review the Attendance and Engagement Policy.\n"
                "- Contact your programme team or student support services if unsure.\n\n"
                "Evidence:\n" + format_sources(sources)
            )
        }

    # COMPLAINTS
    if topic == "complaints":
        return {
            "confidence": "90%",
            "answer": (
                "Summary:\n"
                "Arden University requires students to follow a formal complaints procedure "
                "when raising concerns about services, decisions, or academic processes.\n\n"
                "How complaints are handled:\n"
                "- Complaints are managed through defined procedural stages.\n"
                "- Informal resolution may be encouraged before escalation.\n"
                "- Formal complaints receive an official written response.\n\n"
                "What you should do:\n"
                "- Clearly identify the nature of your complaint.\n"
                "- Review deadlines and evidence requirements in the policy.\n"
                "- Submit your complaint through the official Arden University process.\n\n"
                "Evidence:\n" + format_sources(sources)
            )
        }

    # SAFEGUARDING / INJURY
    if topic == "safeguarding":
        return {
            "confidence": "75%",
            "answer": (
                "Summary:\n"
                "If you are injured or harmed while at university, your safety and wellbeing "
                "are the immediate priority.\n\n"
                "Policy position:\n"
                "- Arden University maintains safeguarding and health & safety arrangements.\n"
                "- Incidents affecting students should be reported via appropriate university channels.\n\n"
                "What you should do next:\n"
                "- Seek immediate medical assistance if required.\n"
                "- Inform university staff or student support services.\n"
                "- Follow guidance under safeguarding or health & safety policies.\n\n"
                "Important note:\n"
                "This information does not replace emergency services or professional medical advice.\n\n"
                "Evidence:\n" + format_sources(sources)
            )
        }

    return {
        "confidence": "40%",
        "answer": "Relevant regulations could not be confidently determined."
    }


def format_sources(sources):
    out = []
    grouped = {}

    for s in sources:
        grouped.setdefault(s["source"], []).append(s["text"])

    for doc, lines in grouped.items():
        out.append(f"From {doc}:")
        for l in lines[:3]:
            out.append(f"- {l}")
        out.append("")

    return "\n".join(out)
