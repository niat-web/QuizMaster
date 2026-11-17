from flask import Blueprint, jsonify, render_template, request

from app import db
from app.models import Attempt, Question, Quiz
from app.validators import get_text, validate_question, validate_quiz

api = Blueprint("api", __name__, url_prefix="/api")
pages = Blueprint("pages", __name__)


def error(message, status):
    return jsonify({"error": message}), status


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
    errors = validate_quiz(data)
    if errors:
        return error(errors[0], 400)

    quiz = Quiz(
        title=get_text(data, "title"),
        description=get_text(data, "description"),
        category=get_text(data, "category") or "General",
        difficulty=get_text(data, "difficulty") or "easy",
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
    errors = validate_question(data)
    if errors:
        return error(errors[0], 400)

    options = [get_text(data, "option_" + letter) for letter in "abcd"]
    question = Question(
        quiz_id=quiz.id,
        text=get_text(data, "text"),
        option_a=options[0],
        option_b=options[1],
        option_c=options[2],
        option_d=options[3],
        correct_option=get_text(data, "correct_option"),
    )
    db.session.add(question)
    db.session.commit()
    return jsonify(question.to_dict()), 201


@api.route("/quizzes/<int:quiz_id>/submit", methods=["POST"])
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