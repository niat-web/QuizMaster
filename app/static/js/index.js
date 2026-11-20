
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
    message.textContent = "Loading quizzes...";

    try {
        const response = await fetch("/api/quizzes");
        if (!response.ok) {
            message.textContent = "Could not load quizzes.";
            return;
        }

        const quizzes = await response.json();
        message.textContent = "";

        if (quizzes.length === 0) {
            message.textContent = "No quizzes yet.";
        }

        quizzes.forEach(showQuiz);
    } catch (error) {
        message.textContent = "Could not load quizzes.";
    }
}

loadQuizzes();
