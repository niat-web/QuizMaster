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
    ["A", "B", "C", "D"].forEach(function (letter) {
        showOption(question, letter);
    });

    prevButton.disabled = currentIndex === 0;
    nextButton.hidden = isLast;
    submitButton.hidden = !isLast;
}


async function submitQuiz() {
    const seconds = Math.round((Date.now() - startTime) / 1000);

    // Prevent multiple submissions
    submitButton.disabled = true;
    message.textContent = "";

    try {
        const response = await fetch("/api/quizzes/" + quizId + "/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                player_name: playerName,
                answers: answers,
                time_taken_seconds: seconds,
            }),
        });

        // Safely parse the server response
        let result;

        try {
            result = await response.json();
        } catch (error) {
            throw new Error(
                "Server returned an invalid response. Please try again."
            );
        }

        // Handle unsuccessful HTTP responses
        if (!response.ok) {
            throw new Error(
                result.error || "Could not submit your answers. Please try again."
            );
        }

        // Submission successful
        result.player_name = playerName;

        sessionStorage.setItem("result", JSON.stringify(result));

        window.location.href = "/result";

    } catch (error) {
        // Show a readable error message
        message.textContent =
            error.message === "Failed to fetch"
                ? "Could not submit your answers. Check your connection and try again."
                : error.message || "Something went wrong. Please try again.";

    } finally {
        // Re-enable the button if the page hasn't navigated away
        submitButton.disabled = false;
    }
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
