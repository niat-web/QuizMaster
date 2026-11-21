const quizId = document.body.dataset.quizId;
const message = document.getElementById("message");
const startForm = document.getElementById("start-form");
const questionBox = document.getElementById("question-box");
const optionsDiv = document.getElementById("options");
const prevButton = document.getElementById("prev-button");
const nextButton = document.getElementById("next-button");
const submitButton = document.getElementById("submit-button");

let quiz = null;
let playerName = "";
let currentIndex = 0;
let startTime = 0;
const answers = {};

async function loadQuiz() {
    const response = await fetch("/api/quizzes/" + quizId);
    if (!response.ok) {
        document.getElementById("quiz-title").textContent = "Quiz";
        message.textContent = "Quiz not found.";
        return;
    }
    quiz = await response.json();
    document.getElementById("quiz-title").textContent = quiz.title;
    document.getElementById("quiz-description").textContent = quiz.description;
    document.getElementById("quiz-category").textContent = quiz.category;
    document.getElementById("quiz-difficulty").textContent = quiz.difficulty;
    document.getElementById("quiz-question-count").textContent = quiz.question_count;
    if (quiz.questions.length === 0) {
        message.textContent = "This quiz has no questions yet.";
        return;
    }
    startForm.hidden = false;
}

function showOption(question, letter) {
    const label = document.createElement("label");
    label.className = "option";

    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "option";
    radio.value = letter;
    radio.checked = answers[question.id] === letter;
    radio.addEventListener("change", function () {
        answers[question.id] = letter;
    });

    const text = document.createElement("span");
    text.textContent = letter + ". " + question["option_" + letter.toLowerCase()];

    label.appendChild(radio);
    label.appendChild(text);
    optionsDiv.appendChild(label);
}

function showQuestion() {

    const question = quiz.questions[currentIndex];
    const isLast = currentIndex === quiz.questions.length - 1;

    document.getElementById("progress").textContent =
        "Question " + (currentIndex + 1) + " of " + quiz.questions.length;
    document.getElementById("question-text").textContent = question.text;

    optionsDiv.innerHTML = "";

    const availableOptions = question.question_type === "true_false"
        ? ["A", "B"]
        : ["A", "B", "C", "D"];

    availableOptions.forEach(function (letter) {
        showOption(question, letter);
    });

    prevButton.disabled = currentIndex === 0;
    nextButton.hidden = isLast;
    submitButton.hidden = !isLast;
}
let quizInProgress = false;

window.addEventListener("beforeunload", (event) => {
    if (quizInProgress) {
        event.preventDefault();
        event.returnValue = "";
    }
});

async function submitQuiz() {
    const seconds = Math.round((Date.now() - startTime) / 1000);
    const response = await fetch("/api/quizzes/" + quizId + "/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            player_name: playerName,
            answers: answers,
            time_taken_seconds: seconds,
        }),
    });
    const result = await response.json();
    if (!response.ok) {
        message.textContent = result.error;
        return;
    }
    result.player_name = playerName;
    sessionStorage.setItem("result", JSON.stringify(result));
    quizInProgress = false;
    window.location.href = "/result";
}

startForm.addEventListener("submit", function (event) {
    event.preventDefault();
    playerName = document.getElementById("player-name").value.trim();
    if (playerName === "") {
        message.textContent = "Please enter your name.";
        return;
    }
    message.textContent = "";
    startForm.hidden = true;
    questionBox.hidden = false;
    startTime = Date.now();
    quizInProgress = true;
    showQuestion();
});

prevButton.addEventListener("click", function () {
    currentIndex = currentIndex - 1;
    showQuestion();
});

nextButton.addEventListener("click", function () {
    currentIndex = currentIndex + 1;
    showQuestion();
});

submitButton.addEventListener("click", submitQuiz);

loadQuiz();
