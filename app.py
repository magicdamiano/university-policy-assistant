from flask import Flask, render_template, request
from retrieve import retrieve
from agent import generate_answer, safety_override

app = Flask(__name__)


# -----------------------------------
# INTENT INFERENCE
# -----------------------------------

INTENT_KEYWORDS = {
    "complaint": ["complaint", "appeal"],
    "safeguarding": ["safeguard", "safety", "health", "risk"],
    "attendance": ["attendance", "engagement", "absence"],
    "misconduct": ["misconduct", "discipline", "conduct"],
    "assessment": ["assessment", "exam", "award", "progression"],
}


def infer_intent(question: str) -> str:
    q = question.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in q for k in keywords):
            return intent
    return "general"


def filter_by_intent(results, intent):
    """
    Remove clearly irrelevant policy excerpts based on intent.
    Conservative by design.
    """
    if intent == "general":
        return results

    allowed = INTENT_KEYWORDS.get(intent, [])
    filtered = []

    for r in results:
        src = r["source"].lower()
        txt = r["text"].lower()
        if any(k in src or k in txt for k in allowed):
            filtered.append(r)

    return filtered


# -----------------------------------
# MAIN ROUTE
# -----------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None

    if request.method == "POST":
        question = request.form.get("question", "").strip()

        if question:
            # STEP 8 — SAFETY OVERRIDE (HARD BOUNDARY)
            safety_response = safety_override(question)
            if safety_response:
                answer = safety_response
            else:
                intent = infer_intent(question)
                retrieved = retrieve(question)
                retrieved = filter_by_intent(retrieved, intent)

                answer = generate_answer(
                    question=question,
                    context=retrieved
                )

    return render_template("index.html", answer=answer)


# -----------------------------------
# APP ENTRY POINT
# -----------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
