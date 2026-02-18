from flask import Flask, render_template, request
from retrieve import retrieve
from agent import ask_agent

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None

    if request.method == "POST":
        question = request.form.get("question", "").strip()
        print("[app] question:", question)

        if question:
            docs = retrieve(question)
            print("[app] retrieved:", len(docs))

            answer = ask_agent(question, docs)
            print("[app] answer generated")

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
