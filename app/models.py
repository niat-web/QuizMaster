
from datetime import datetime, timezone

from app import db


def utc_now():
    return datetime.now(timezone.utc)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), default="")
    category = db.Column(db.String(50), default="General")
    difficulty = db.Column(db.String(10), default="easy")
    created_at = db.Column(db.DateTime, default=utc_now)

    questions = db.relationship(
        "Question", backref="quiz", lazy=True, cascade="all, delete-orphan"
    )
    attempts = db.relationship(
        "Attempt", backref="quiz", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self, question_count=None):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "difficulty": self.difficulty,
            "question_count": (
                len(self.questions)
                if question_count is None
                else question_count
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quiz.id"), nullable=False, index=True
    )
    text = db.Column(db.String(255), nullable=False)

    question_type = db.Column(
        db.String(20),
        nullable=False,
        default="multiple_choice",
        server_default="multiple_choice",
    )

    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=True)
    option_d = db.Column(db.String(100), nullable=True)

    correct_option = db.Column(db.String(1), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        # The correct answer is not included on purpose.
        result = {
            "id": self.id,
            "text": self.text,
            "question_type": self.question_type,
            "option_a": self.option_a,
            "option_b": self.option_b,
        }

        if self.question_type == "multiple_choice":
            result["option_c"] = self.option_c
            result["option_d"] = self.option_d

        return result


class Attempt(db.Model):
    __table_args__ = (
        db.Index(
            "ix_attempt_leaderboard",
            "quiz_id",
            db.desc("score"),
            "time_taken_seconds",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    player_name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    time_taken_seconds = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "quiz_title": self.quiz.title if self.quiz else "",
            "player_name": self.player_name,
            "score": self.score,
            "total_questions": self.total_questions,
            "time_taken_seconds": self.time_taken_seconds,
            "created_at": self.created_at.isoformat(),
        }
