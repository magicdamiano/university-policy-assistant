from flask import Flask, render_template, request, jsonify
from retrieve import retrieve_with_scores
from agent import answer

app = Flask(__name__)

# ==================================================
# ROUTES
# ==================================================

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    # -- Input validation --
    question = request.form.get("question", "").strip()

    if not question:
        return jsonify({
            "success": False,
            "error": "Please enter a question."
        }), 400

    if len(question) > 1000:
        return jsonify({
            "success": False,
            "error": "Question is too long. Please keep it under 1000 characters."
        }), 400

    # -- Retrieve + answer --
    try:
        context, scores = retrieve_with_scores(question)
        raw_answer = answer(question, context, scores)
    except Exception as e:
        app.logger.error(f"Error processing question: {e}")
        return jsonify({
            "success": False,
            "error": "An internal error occurred. Please try again."
        }), 500

    # -- Parse confidence out of the answer string --
    confidence = _extract_confidence(raw_answer)
    answer_body = _strip_confidence_line(raw_answer)

    # -- Build sources list from context --
    sources = _build_sources(context)

    return jsonify({
        "success": True,
        "answer": answer_body,
        "confidence": confidence,
        "sources": sources,
    })


# ==================================================
# HELPERS
# ==================================================

def _extract_confidence(text: str) -> int:
    """Pull the integer confidence value out of the answer string."""
    import re
    match = re.search(r"Confidence:\s*(\d+)%", text)
    return int(match.group(1)) if match else 0


def _strip_confidence_line(text: str) -> str:
    """Remove the 'Confidence: X%' line from the answer body."""
    import re
    return re.sub(r"Confidence:\s*\d+%\n*", "", text).strip()


def _build_sources(context: list) -> list:
    """
    Return a deduplicated list of {policy, section} dicts
    for the chunks that were actually used.
    """
    seen = set()
    sources = []
    for c in context:
        key = (c["policy"], c["section"])
        if key not in seen:
            seen.add(key)
            sources.append({
                "policy": c["policy"],
                "section": c["section"],
            })
    return sources


# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
