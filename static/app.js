const form = document.getElementById("ask-form");
const textarea = document.getElementById("question");
const answerBox = document.getElementById("answer-box");
const answerContent = document.getElementById("answer-content");
const loading = document.getElementById("loading");
const confidenceBadge = document.getElementById("confidence-badge");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const question = textarea.value.trim();
    if (!question) return;

    answerBox.classList.add("hidden");
    loading.classList.remove("hidden");
    confidenceBadge.textContent = "";

    const formData = new FormData();
    formData.append("question", question);

    try {
        const response = await fetch("/ask", {
            method: "POST",
            body: formData
        });

        const text = await response.text();

        // Extract confidence
        const match = text.match(/Confidence:\s*(\d+)%/);
        if (match) {
            confidenceBadge.textContent = `Confidence: ${match[1]}%`;
            confidenceBadge.className = "confidence confidence-" + level(match[1]);
        }

        answerContent.textContent = text;
        loading.classList.add("hidden");
        answerBox.classList.remove("hidden");
        answerBox.classList.add("fade-in");

    } catch (err) {
        loading.textContent = "An error occurred. Please try again.";
    }
});

function level(value) {
    value = parseInt(value);
    if (value >= 75) return "high";
    if (value >= 50) return "medium";
    return "low";
}
