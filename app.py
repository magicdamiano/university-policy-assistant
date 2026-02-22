from flask import Flask, render_template, request
from retrieve import retrieve
from agent import generate_answer

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()
    if not question:
        return "Please enter a question."

    context = retrieve(question)
    answer = generate_answer(question, context)
    return answer


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
