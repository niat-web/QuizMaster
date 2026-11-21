from flask import Blueprint, current_app, jsonify, render_template, request

from app import db, limiter
from app.models import Attempt, Question, Quiz

api = Blueprint("api", __name__, url_prefix="/api")
pages = Blueprint("pages", __name__)

DIFFICULTIES = ["easy", "medium", "hard"]
OPTIONS = {
    "multiple_choice": ["A", "B", "C", "D"],
    "true_false": ["A", "B"],
}


def error(message, status):
    return jsonify({"error": message}), status


def get_text(data, field):
    # Returns the field as a trimmed string, or "" if it is missing
    value = data.get(field)
    if not isinstance(value, str):
        return ""
    return value.strip()


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


@pages.route("/history")
def history_page():
    return render_template("history.html")


@api.route("/quizzes")
def list_quizzes():
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")

    question_counts = (
        db.session.query(
            Question.quiz_id,
            db.func.count(Question.id).label("count"),
        )
        .group_by(Question.quiz_id)
        .subquery()
    )

    query = db.session.query(
        Quiz,
        db.func.coalesce(question_counts.c.count, 0).label("question_count"),
    ).outerjoin(
        question_counts,
        Quiz.id == question_counts.c.quiz_id,
    )

    if category:
        query = query.filter(Quiz.category == category)
    if difficulty:
        query = query.filter(Quiz.difficulty == difficulty)

    results = query.order_by(Quiz.id).all()
    return jsonify([
        quiz.to_dict(question_count=int(q_count)) for quiz, q_count in results
    ])


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
    raw_question_type = data.get("question_type", "multiple_choice")

    if not isinstance(raw_question_type, str):
        return error("question_type must be a string", 400)

    question_type = raw_question_type.strip()

    if question_type not in OPTIONS:
        return error(
            "question_type must be multiple_choice or true_false",
            400
        )
    options = {
        letter: get_text(data, "option_" + letter.lower())
        for letter in OPTIONS[question_type]
    }

    if not text:
        return error("Question text is required", 400)

    if any(not value for value in options.values()):
        return error("All options for this question type are required", 400)

    if question_type == "true_false":
        if get_text(data, "option_c") or get_text(data, "option_d"):
            return error("True/false questions can only have two options", 400)

    correct_option = get_text(data, "correct_option")
    if correct_option not in OPTIONS[question_type]:
        allowed = " or ".join(OPTIONS[question_type])
        return error(f"correct_option must be {allowed}", 400)

    question = Question(
        quiz_id=quiz.id,
        text=text,
        question_type=question_type,
        option_a=options["A"],
        option_b=options["B"],
        option_c=options.get("C"),
        option_d=options.get("D"),
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
    if len(player_name) > 30:
        return error("Player name cannot exceed 30 characters", 400)
    if not isinstance(answers, dict):
        return error("Answers must be an object like {\"1\": \"A\"}", 400)
    if isinstance(time_taken, bool) or not isinstance(time_taken, int) or time_taken < 0:
        return error("time_taken_seconds must be a positive number", 400)

       # Answers are keyed by question id; unanswered questions count as wrong.
    # Only valid options for each question type can receive credit.
    score = 0
    for question in quiz.questions:
        submitted_answer = answers.get(str(question.id))
        valid_options = OPTIONS.get(question.question_type, [])

        if (
            submitted_answer in valid_options
            and submitted_answer == question.correct_option
        ):
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
    attempt_stats = (
        db.session.query(
            Attempt.quiz_id,
            db.func.count(Attempt.id).label("attempt_count"),
            db.func.avg(Attempt.score).label("avg_score"),
        )
        .group_by(Attempt.quiz_id)
        .subquery()
    )

    rows = (
        db.session.query(
            Quiz.id,
            Quiz.title,
            db.func.coalesce(
                attempt_stats.c.attempt_count, 0
            ).label("attempts"),
            attempt_stats.c.avg_score,
        )
        .outerjoin(attempt_stats, Quiz.id == attempt_stats.c.quiz_id)
        .order_by(Quiz.id)
        .all()
    )

    quiz_stats = []
    for quiz_id, title, attempts, avg_score in rows:
        quiz_stats.append({
            "quiz_id": quiz_id,
            "title": title,
            "attempts": int(attempts),
            "average_score": round(avg_score or 0, 2),
        })

    return jsonify({
        "total_quizzes": len(rows),
        "total_attempts": Attempt.query.count(),
        "quizzes": quiz_stats,
    })


@api.route("/players/<player_name>/attempts")
def player_attempts(player_name):
    name = (player_name or "").strip()
    if not name:
        return error("Player name is required", 400)
    attempts = (
        Attempt.query.filter(
            db.func.lower(Attempt.player_name) == name.lower()
        )
        .order_by(Attempt.created_at.desc(), Attempt.id.desc())
        .all()
    )
    return jsonify([attempt.to_dict() for attempt in attempts])


