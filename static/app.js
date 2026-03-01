// ==================================================
// ELEMENTS
// ==================================================

const form            = document.getElementById("ask-form");
const textarea        = document.getElementById("question");
const answerBox       = document.getElementById("answer-box");
const answerContent   = document.getElementById("answer-content");
const loading         = document.getElementById("loading");
const confidenceBadge = document.getElementById("confidence-badge");
const sourcesBox      = document.getElementById("sources-box");
const copyBtn         = document.getElementById("copy-btn");
const historyList     = document.getElementById("history-list");
const charCount       = document.getElementById("char-count");

const MAX_CHARS = 1000;
const MAX_HISTORY = 8;

// In-memory question history for this session
let history = [];

// ==================================================
// CHAR COUNTER
// ==================================================

textarea.addEventListener("input", () => {
  const len = textarea.value.length;
  charCount.textContent = `${len} / ${MAX_CHARS}`;
  charCount.classList.toggle("char-limit", len >= MAX_CHARS);
});

// ==================================================
// FORM SUBMIT
// ==================================================

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = textarea.value.trim();
  if (!question) return;

  // UI: loading state
  answerBox.classList.add("hidden");
  loading.classList.remove("hidden");
  confidenceBadge.textContent = "";
  sourcesBox.innerHTML = "";

  const formData = new FormData();
  formData.append("question", question);

  try {
    const response = await fetch("/ask", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    loading.classList.add("hidden");

    if (!data.success) {
      showError(data.error || "An unexpected error occurred.");
      return;
    }

    renderAnswer(data, question);
    addToHistory(question, data);

  } catch (err) {
    loading.classList.add("hidden");
    showError("Could not reach the server. Please check your connection.");
  }
});

// ==================================================
// RENDER ANSWER
// ==================================================

function renderAnswer(data, question) {
  // Confidence badge
  const level = confidenceLevel(data.confidence);
  confidenceBadge.textContent = `Confidence: ${data.confidence}%`;
  confidenceBadge.className = `confidence confidence-${level}`;

  // Answer body — convert bullet lines to <li>, preserve line breaks
  answerContent.innerHTML = formatAnswer(data.answer);

  // Sources chips
  sourcesBox.innerHTML = "";
  if (data.sources && data.sources.length > 0) {
    const label = document.createElement("p");
    label.className = "sources-label";
    label.textContent = "Sources:";
    sourcesBox.appendChild(label);

    const chipWrap = document.createElement("div");
    chipWrap.className = "sources-chips";

    data.sources.forEach(s => {
      const chip = document.createElement("span");
      chip.className = "source-chip";
      chip.textContent = `${s.policy} — ${s.section}`;
      chip.title = `${s.policy}: ${s.section}`;
      chipWrap.appendChild(chip);
    });

    sourcesBox.appendChild(chipWrap);
  }

  // Show answer box
  answerBox.classList.remove("hidden");
  answerBox.classList.add("fade-in");

  // Scroll into view smoothly
  answerBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ==================================================
// FORMAT ANSWER TEXT → HTML
// ==================================================

function formatAnswer(text) {
  const lines = text.split("\n");
  let html = "";
  let inList = false;

  lines.forEach(line => {
    const trimmed = line.trim();

    if (trimmed.startsWith("- ")) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${escapeHtml(trimmed.slice(2))}</li>`;
    } else {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      if (trimmed === "") {
        html += "<br>";
      } else {
        html += `<p>${escapeHtml(trimmed)}</p>`;
      }
    }
  });

  if (inList) html += "</ul>";
  return html;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ==================================================
// COPY BUTTON
// ==================================================

copyBtn.addEventListener("click", () => {
  const text = answerContent.innerText;
  navigator.clipboard.writeText(text).then(() => {
    copyBtn.textContent = "Copied!";
    setTimeout(() => { copyBtn.textContent = "Copy answer"; }, 2000);
  }).catch(() => {
    copyBtn.textContent = "Copy failed";
    setTimeout(() => { copyBtn.textContent = "Copy answer"; }, 2000);
  });
});

// ==================================================
// QUESTION HISTORY
// ==================================================

function addToHistory(question, data) {
  // Prepend to front, cap at MAX_HISTORY
  history.unshift({ question, confidence: data.confidence });
  if (history.length > MAX_HISTORY) history.pop();
  renderHistory();
}

function renderHistory() {
  if (!historyList) return;
  historyList.innerHTML = "";

  history.forEach((item, idx) => {
    const li = document.createElement("li");
    li.className = "history-item";

    const q = document.createElement("span");
    q.className = "history-question";
    q.textContent = item.question.length > 60
      ? item.question.slice(0, 60) + "…"
      : item.question;

    const badge = document.createElement("span");
    badge.className = `history-badge confidence-${confidenceLevel(item.confidence)}`;
    badge.textContent = `${item.confidence}%`;

    li.appendChild(q);
    li.appendChild(badge);

    // Click to re-ask
    li.addEventListener("click", () => {
      textarea.value = item.question;
      textarea.dispatchEvent(new Event("input")); // update char count
      textarea.focus();
    });

    historyList.appendChild(li);
  });
}

// ==================================================
// ERROR DISPLAY
// ==================================================

function showError(message) {
  answerContent.innerHTML = `<p class="error-msg">${escapeHtml(message)}</p>`;
  confidenceBadge.textContent = "";
  sourcesBox.innerHTML = "";
  answerBox.classList.remove("hidden");
}

// ==================================================
// UTILITIES
// ==================================================

function confidenceLevel(value) {
  value = parseInt(value);
  if (value >= 75) return "high";
  if (value >= 50) return "medium";
  return "low";
}
