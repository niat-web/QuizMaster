const message = document.getElementById("message");
const quizForm = document.getElementById("quiz-form");
const questionForm = document.getElementById("question-form");
const questionCount = document.getElementById("question-count");

let quizId = null;
let added = 0;

async function postJson(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.error || "Request failed");
    }
    return result;
}

quizForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    message.textContent = "";
    try {
        const quiz = await postJson("/api/quizzes", {
            title: document.getElementById("quiz-title").value,
            description: document.getElementById("quiz-description").value,
            category: document.getElementById("quiz-category").value,
            difficulty: document.getElementById("quiz-difficulty").value,
        });
        quizId = quiz.id;
        quizForm.hidden = true;
        questionForm.hidden = false;
        message.textContent = "Quiz created. Now add questions.";
    } catch (err) {
        message.textContent = err.message;
    }
});

questionForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    message.textContent = "";
    try {
        await postJson("/api/quizzes/" + quizId + "/questions", {
            text: document.getElementById("question-text").value,
            option_a: document.getElementById("option-a").value,
            option_b: document.getElementById("option-b").value,
            option_c: document.getElementById("option-c").value,
            option_d: document.getElementById("option-d").value,
            correct_option: document.getElementById("correct-option").value,
        });
        added += 1;
        questionCount.textContent = added + " question(s) added.";
        questionForm.reset();
    } catch (err) {
        message.textContent = err.message;
    }
});