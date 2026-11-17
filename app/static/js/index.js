const quizList = document.getElementById("quiz-list");
const quizOfTheDayContainer = document.getElementById("quiz-of-the-day");
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

function showQuizOfTheDay(quiz) {
    if (!quizOfTheDayContainer) {
        return;
    }
    quizOfTheDayContainer.innerHTML = "";

    const card = document.createElement("div");
    card.className = "card highlighted-card highlighted quiz-of-the-day";

    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = "Quiz of the day";
    card.appendChild(badge);

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

    quizOfTheDayContainer.appendChild(card);
}

async function loadQuizOfTheDay() {
    try {
        const response = await fetch("/api/quiz-of-the-day");
        if (!response.ok) {
            return;
        }
        const quiz = await response.json();
        showQuizOfTheDay(quiz);
    } catch {
        // Keep home page working if the request fails
    }
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

loadQuizOfTheDay();
loadQuizzes();
