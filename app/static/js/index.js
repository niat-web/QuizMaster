
const quizList = document.getElementById("quiz-list");
const quizOfTheDayContainer = document.getElementById("quiz-of-the-day");
const message = document.getElementById("message");
const searchInput = document.getElementById("search-input");
const noResults = document.getElementById("no-results");

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
    card.dataset.title = quiz.title;
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
    const query = searchInput.value.trim().toLowerCase();
    const cards = quizList.querySelectorAll(".card");
    let visibleCount = 0;

    cards.forEach(function (card) {
        const title = (card.dataset.title || (card.querySelector("h2") ? card.querySelector("h2").textContent : "")).toLowerCase();
        if (query === "" || title.includes(query)) {
            card.hidden = false;
            visibleCount++;
        } else {
            card.hidden = true;
        }
    });

    if (noResults) {
        if (cards.length > 0 && query !== "" && visibleCount === 0) {
            noResults.hidden = false;
        } else {
            noResults.hidden = true;
        }
    }
}

if (searchInput) {
    searchInput.addEventListener("input", filterQuizzes);
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
        filterQuizzes();
    } catch (error) {
        message.textContent = "Could not load quizzes.";
    }
}

loadQuizOfTheDay();
loadQuizzes();
