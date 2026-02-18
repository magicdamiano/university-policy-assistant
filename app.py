from flask import Flask, render_template, request
from retrieve import retrieve
from agent import ask_agent

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    confidence = None
    question = None

    if request.method == "POST":
        question = request.form.get("question", "").strip()
        sources = retrieve(question)
        result = ask_agent(question, sources)

        answer = result["answer"]
        confidence = result["confidence"]

    return render_template(
        "index.html",
        answer=answer,
        confidence=confidence,
        question=question
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
