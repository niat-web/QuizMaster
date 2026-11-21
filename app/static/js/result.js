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
const wrongAnswers = result.wrong_answers || [];

if (wrongAnswers.length > 0) {
    const section = document.getElementById("wrong-answers-section");
    const list = document.getElementById("wrong-answers-list");

    section.hidden = false;

    wrongAnswers.forEach(function (item, index) {
        const card = document.createElement("div");
        card.className = "card";

        const question = document.createElement("h3");
        question.textContent = (index + 1) + ". " + item.question;

        const yourAnswer = document.createElement("p");
        yourAnswer.textContent = "Your answer: " + item.your_answer;

        const correctAnswer = document.createElement("p");
        correctAnswer.textContent = "Correct answer: " + item.correct_answer;

        card.appendChild(question);
        card.appendChild(yourAnswer);
        card.appendChild(correctAnswer);

        list.appendChild(card);
    });
}
        document.getElementById("result-box").hidden = false;
}
