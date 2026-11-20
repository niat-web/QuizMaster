import re
from flask import Blueprint, current_app, jsonify, render_template, request

from app import db, limiter
from app.models import Attempt, Question, Quiz

api = Blueprint("api", __name__, url_prefix="/api")
pages = Blueprint("pages", __name__)

DIFFICULTIES = ["easy", "medium", "hard"]
OPTIONS = ["A", "B", "C", "D"]


def error(message, status):
    return jsonify({"error": message}), status


def get_text(data, field):
    # Returns the field as a trimmed string, or "" if it is missing
    value = data.get(field)
    if not isinstance(value, str):
        return ""
    return value.strip()


def normalize_question_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


@pages.route("/")
def index():
    return render_template("index.html")


@pages.route("/quiz/<int:quiz_id>")
def quiz_page(quiz_id):
    return render_template("quiz.html", quiz_id=quiz_id)


@pages.route("/result")
def result_page():
    return render_template("result.html")


@pages.route("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html")

@pages.app_errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return error("Not found", 404)
    return render_template("404.html"), 404


@pages.route("/create")
def create_page():
    return render_template("create.html")


@api.route("/quizzes")
def list_quizzes():
    query = Quiz.query
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    quizzes = query.order_by(Quiz.id).all()
    return jsonify([quiz.to_dict() for quiz in quizzes])


@api.route("/quizzes/<int:quiz_id>")
def get_quiz(quiz_id):
    quiz = db.session.get(Quiz, quiz_id)
    if quiz is None:
        return error("Quiz not found", 404)
    data = quiz.to_dict()
    data["questions"] = [question.to_dict() for question in quiz.questions]
    return jsonify(data)


@api.route("/quizzes", methods=["POST"])
def create_quiz():
    data = request.get_json(silent=True) or {}
    title = get_text(data, "title")
    difficulty = get_text(data, "difficulty") or "easy"
    if not title:
        return error("Title is required", 400)
    if difficulty not in DIFFICULTIES:
        return error("Difficulty must be easy, medium or hard", 400)

    existing_quiz = Quiz.query.filter(db.func.lower(Quiz.title) == title.lower()).first()
    if existing_quiz:
        return error("A quiz with this title already exists", 400)

    quiz = Quiz(
        title=title,
        description=get_text(data, "description"),
        category=get_text(data, "category") or "General",
        difficulty=difficulty,
    )
    db.session.add(quiz)
    db.session.commit()
    return jsonify(quiz.to_dict()), 201


@api.route("/quizzes/<int:quiz_id>/questions", methods=["POST"])
def add_question(quiz_id):
    quiz = db.session.get(Quiz, quiz_id)
    if quiz is None:
        return error("Quiz not found", 404)

    data = request.get_json(silent=True) or {}
    text = get_text(data, "text")
    options = [get_text(data, "option_" + letter) for letter in "abcd"]
    correct_option = get_text(data, "correct_option")
    if not text or "" in options:
        return error("Question text and all 4 options are required", 400)
    if correct_option not in OPTIONS:
        return error("correct_option must be A, B, C or D", 400)

    normalized_text = normalize_question_text(text)
    existing_questions = db.session.scalars(
        db.select(Question).filter_by(quiz_id=quiz.id)
    )
    if any(normalize_question_text(q.text) == normalized_text for q in existing_questions):
        return error("This question already exists in this quiz", 409)

    question = Question(
        quiz_id=quiz.id,
        text=text,
        option_a=options[0],
        option_b=options[1],
        option_c=options[2],
        option_d=options[3],
        correct_option=correct_option,
    )
    db.session.add(question)
    db.session.commit()
    return jsonify(question.to_dict()), 201


@api.route("/quizzes/<int:quiz_id>/submit", methods=["POST"])
@limiter.limit(lambda: current_app.config["SUBMIT_RATE_LIMIT"])
def submit_quiz(quiz_id):
    quiz = db.session.get(Quiz, quiz_id)
    if quiz is None:
        return error("Quiz not found", 404)
    if not quiz.questions:
        return error("This quiz has no questions", 400)

    data = request.get_json(silent=True) or {}
    player_name = get_text(data, "player_name")
    answers = data.get("answers")
    time_taken = data.get("time_taken_seconds", 0)
    if not player_name:
        return error("Player name is required", 400)
    if not isinstance(answers, dict):
        return error("Answers must be an object like {\"1\": \"A\"}", 400)
    if not isinstance(time_taken, int) or time_taken < 0:
        return error("time_taken_seconds must be a positive number", 400)

    # Answers are keyed by question id; unanswered questions count as wrong
    score = 0
    for question in quiz.questions:
        if answers.get(str(question.id)) == question.correct_option:
            score += 1
    total = len(quiz.questions)

    attempt = Attempt(
        quiz_id=quiz.id,
        player_name=player_name,
        score=score,
        total_questions=total,
        time_taken_seconds=time_taken,
    )
    db.session.add(attempt)
    db.session.commit()
    return jsonify({
        "attempt_id": attempt.id,
        "quiz_id": quiz.id,
        "score": score,
        "total_questions": total,
        "correct": score,
        "wrong": total - score,
        "time_taken_seconds": time_taken,
    })


@api.route("/quizzes/<int:quiz_id>/leaderboard")
def leaderboard(quiz_id):
    quiz = db.session.get(Quiz, quiz_id)
    if quiz is None:
        return error("Quiz not found", 404)
    attempts = (
        Attempt.query.filter_by(quiz_id=quiz_id)
        .order_by(Attempt.score.desc(), Attempt.time_taken_seconds)
        .limit(10)
        .all()
    )
    return jsonify([attempt.to_dict() for attempt in attempts])


@api.route("/stats")
def stats():
    quiz_stats = []
    for quiz in Quiz.query.order_by(Quiz.id).all():
        average = db.session.query(db.func.avg(Attempt.score)).filter(
            Attempt.quiz_id == quiz.id
        ).scalar()
        quiz_stats.append({
            "quiz_id": quiz.id,
            "title": quiz.title,
            "attempts": len(quiz.attempts),
            "average_score": round(average or 0, 2),
        })
    return jsonify({
        "total_quizzes": Quiz.query.count(),
        "total_attempts": Attempt.query.count(),
        "quizzes": quiz_stats,
    })
