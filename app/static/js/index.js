const quizList = document.getElementById("quiz-list");
const message = document.getElementById("message");

function addLine(parent, tag, text, className) {
    const element = document.createElement(tag);
    element.textContent = text;
    if (className) {
        element.className = className;
    }
    parent.appendChild(element);
}

function showQuiz(quiz) {
    const card = document.createElement("div");
    card.className = "card";
    addLine(card, "h2", quiz.title);
    addLine(card, "p", quiz.description);
    addLine(card, "p", "Category: " + quiz.category);
    addLine(card, "p", "Difficulty: " + quiz.difficulty);
    addLine(card, "p", "Questions: " + quiz.question_count);

    const link = document.createElement("a");
    link.className = "button";
    link.href = "/quiz/" + quiz.id;
    link.textContent = "Open quiz";
    card.appendChild(link);
    quizList.appendChild(card);
}

async function loadQuizzes() {
    const response = await fetch("/api/quizzes");
    if (!response.ok) {
        message.textContent = "Could not load quizzes.";
        return;
    }
    const quizzes = await response.json();
    if (quizzes.length === 0) {
        message.textContent = "No quizzes yet.";
    }
    quizzes.forEach(showQuiz);
}

loadQuizzes();

const mixedForm = document.getElementById("mixed-quiz-form");
if (mixedForm) {
    mixedForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const category = document.getElementById("mixed-category").value;
        const difficulty = document.getElementById("mixed-difficulty").value;

        const body = {};
        if (category) body.category = category;
        if (difficulty) body.difficulty = difficulty;

        const response = await fetch("/api/quizzes/mixed", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        const result = await response.json();
        if (!response.ok) {
            alert(result.error || "Could not generate mixed quiz.");
            return;
        }

        window.location.href = "/quiz/" + result.id;
    });
}

