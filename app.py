from flask import Flask, render_template, request
from retrieve import retrieve
from agent import ask_agent

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    response = None
    question = ""

    if request.method == "POST":
        question = request.form.get("question", "").strip()

        if question:
            docs = retrieve(question, top_k=3)

            answer_text = ask_agent(question, docs)

            response = {
                "answer": answer_text,
                "confidence": 0.7 if docs else 0.0,
                "sources": docs
            }

    return render_template(
        "index.html",
        question=question,
        response=response
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
