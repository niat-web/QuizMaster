const message = document.getElementById("message");
const historyForm = document.getElementById("history-form");
const playerNameInput = document.getElementById("player-name");
const historyTable = document.getElementById("history-table");
const tableBody = document.getElementById("history-body");

function addCell(row, text) {
    const cell = document.createElement("td");
    cell.textContent = text;
    row.appendChild(cell);
}

function formatDate(isoString) {
    if (!isoString) {
        return "";
    }
    const date = new Date(isoString);
    if (isNaN(date.getTime())) {
        return isoString;
    }
    return date.toLocaleString();
}

async function loadHistory(name) {
    const trimmed = (name || "").trim();
    tableBody.innerHTML = "";

    if (trimmed === "") {
        message.textContent = "Please enter a player name.";
        historyTable.hidden = true;
        return;
    }

    message.textContent = "";
    try {
        const response = await fetch("/api/players/" + encodeURIComponent(trimmed) + "/attempts");
        if (!response.ok) {
            const data = await response.json().catch(function () { return {}; });
            message.textContent = data.error || "Could not load history.";
            historyTable.hidden = true;
            return;
        }
        const attempts = await response.json();
        if (attempts.length === 0) {
            message.textContent = 'No attempts found for "' + trimmed + '".';
            historyTable.hidden = true;
            return;
        }

        attempts.forEach(function (attempt) {
            const row = document.createElement("tr");
            addCell(row, attempt.quiz_title || ("Quiz " + attempt.quiz_id));
            addCell(row, attempt.score + " / " + attempt.total_questions);
            addCell(row, attempt.time_taken_seconds);
            addCell(row, formatDate(attempt.created_at));
            tableBody.appendChild(row);
        });
        historyTable.hidden = false;
    } catch (err) {
        message.textContent = "Failed to fetch attempt history.";
        historyTable.hidden = true;
    }
}

historyForm.addEventListener("submit", function (event) {
    event.preventDefault();
    loadHistory(playerNameInput.value);
});

const params = new URLSearchParams(window.location.search);
const initialName = params.get("player") || params.get("name");
if (initialName) {
    playerNameInput.value = initialName;
    loadHistory(initialName);
}
