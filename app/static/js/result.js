const message = document.getElementById("message");
const saved = sessionStorage.getItem("result");

if (saved === null) {
    message.textContent = "No result found. Take a quiz first.";
} else {
    const result = JSON.parse(saved);
    document.getElementById("result-name").textContent = "Well done, " + result.player_name;
    document.getElementById("result-score").textContent =
        "You scored " + result.score + " out of " + result.total_questions;
    document.getElementById("result-correct").textContent = "Correct answers: " + result.correct;
    document.getElementById("result-wrong").textContent = "Wrong answers: " + result.wrong;
    document.getElementById("result-time").textContent =
        "Time taken: " + result.time_taken_seconds + " seconds";
    document.getElementById("leaderboard-link").href = "/leaderboard?quiz=" + result.quiz_id;
    document.getElementById("history-link").href = "/history?name=" + encodeURIComponent(result.player_name);
    document.getElementById("result-box").hidden = false;
}
