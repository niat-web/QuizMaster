const message = document.getElementById("message");
const quizSelect = document.getElementById("quiz-select");
const tableBody = document.getElementById("leaderboard-body");

function addCell(row, text) {
    const cell = document.createElement("td");
    cell.textContent = text;
    row.appendChild(cell);
}

async function loadLeaderboard() {
    tableBody.innerHTML = "";
    message.textContent = "";
    const response = await fetch("/api/quizzes/" + quizSelect.value + "/leaderboard");
    if (!response.ok) {
        message.textContent = "Could not load the leaderboard.";
        return;
    }
    const attempts = await response.json();
    if (attempts.length === 0) {
        message.textContent = "No attempts yet for this quiz.";
    }
    attempts.forEach(function (attempt, index) {
        const row = document.createElement("tr");
        addCell(row, index + 1);
        addCell(row, attempt.player_name);
        addCell(row, attempt.score + " / " + attempt.total_questions);
        addCell(row, attempt.time_taken_seconds);
        tableBody.appendChild(row);
    });
}


async function loadQuizzes() {
    try {
        const response = await fetch("/api/quizzes");

        if (!response.ok) {
            message.textContent = "Could not load quizzes.";
            return;
        }

        const quizzes = await response.json();

        if (quizzes.length === 0) {
            message.textContent = "No quizzes yet.";
            return;
        }

        quizzes.forEach(function (quiz) {
            const option = document.createElement("option");
            option.value = quiz.id;
            option.textContent = quiz.title;
            quizSelect.appendChild(option);
        });

        // The result page links here with ?quiz=<id>
        const wantedId = new URLSearchParams(window.location.search).get("quiz");
        if (wantedId) {
            quizSelect.value = wantedId;
        }

        loadLeaderboard();

    } catch (error) {
        message.textContent = "Could not load quizzes.";
    }
}


quizSelect.addEventListener("change", loadLeaderboard);

loadQuizzes();
