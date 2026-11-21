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
let quizMode = "normal";
const answers = {};
const practiceFeedback = {};

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
    radio.disabled = quizMode === "practice" && Boolean(practiceFeedback[question.id]);
    radio.addEventListener("change", function () {
        answers[question.id] = letter;
        if (quizMode === "practice") {
            const radios = optionsDiv.querySelectorAll('input[name="option"]');
            radios.forEach(function (option) {
                option.disabled = true;
            });
            checkPracticeAnswer(question, letter);
    }
});
    const text = document.createElement("span");
    text.textContent = letter + ". " + question["option_" + letter.toLowerCase()];

    label.appendChild(radio);
    label.appendChild(text);
    optionsDiv.appendChild(label);
}
    async function checkPracticeAnswer(question, answer) {
    const feedbackBox = document.getElementById("practice-feedback");
    const resultText = document.getElementById("feedback-result");
    const correctAnswerText = document.getElementById("feedback-correct-answer");
    const explanationText = document.getElementById("feedback-explanation");

    feedbackBox.hidden = false;
    resultText.textContent = "Checking your answer...";
    correctAnswerText.textContent = "";
    explanationText.textContent = "";

    try {
        const response = await fetch(
            "/api/quizzes/" + quizId + "/questions/" + question.id + "/check",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ answer: answer }),
            }
        );

        const result = await response.json();

        if (!response.ok) {
            resultText.textContent = result.error || "Could not check your answer.";
            return;
        }

        resultText.textContent = result.correct
            ? "Correct! Well done."
            : "Not quite. Keep learning!";

        correctAnswerText.textContent =
            "Correct answer: " + result.correct_option;

        explanationText.textContent =
            result.explanation || "No explanation is available for this question.";

        practiceFeedback[question.id] = result;
    } catch (error) {
        resultText.textContent = "Unable to check your answer. Please try again.";
    }
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
    const feedbackBox = document.getElementById("practice-feedback");

if (quizMode === "practice" && practiceFeedback[question.id]) {
    const feedback = practiceFeedback[question.id];

    feedbackBox.hidden = false;
    document.getElementById("feedback-result").textContent =
        feedback.correct ? "Correct! Well done." : "Not quite. Keep learning!";

    document.getElementById("feedback-correct-answer").textContent =
        "Correct answer: " + feedback.correct_option;

    document.getElementById("feedback-explanation").textContent =
        feedback.explanation || "No explanation is available for this question.";
} else {
    feedbackBox.hidden = true;
}

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
        if (quizMode === "practice") {
        quizInProgress = false;
        questionBox.hidden = true;
        message.textContent = "Practice completed! Great work. You can review what you learned.";
        return;
    }
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
    quizMode = document.querySelector('input[name="quiz-mode"]:checked').value;
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
