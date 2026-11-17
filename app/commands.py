import json
import sys

import click
from flask.cli import with_appcontext

from app import db
from app.models import Question, Quiz
from app.validators import get_text, validate_question, validate_quiz


@click.command("import-quiz")
@click.argument("filepath")
@with_appcontext
def import_quiz_command(filepath):
    """Import a quiz and its questions from a JSON file."""
    # Read and parse the file
    try:
        with open(filepath) as f:
            data = json.load(f)
    except FileNotFoundError:
        click.echo(f"Error: file '{filepath}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as exc:
        click.echo(f"Error: invalid JSON — {exc}")
        sys.exit(1)

    # Validate quiz-level fields
    quiz_errors = validate_quiz(data)
    if quiz_errors:
        for msg in quiz_errors:
            click.echo(f"Error: {msg}")
        sys.exit(1)

    #  Validate the questions list
    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) == 0:
        click.echo("Error: 'questions' must be a non-empty list.")
        sys.exit(1)

    all_errors = []
    for i, q in enumerate(questions):
        all_errors.extend(validate_question(q, index=i))

    if all_errors:
        for msg in all_errors:
            click.echo(f"Error: {msg}")
        sys.exit(1)

    #  All valid — save everything in one go
    quiz = Quiz(
        title=get_text(data, "title"),
        description=get_text(data, "description"),
        category=get_text(data, "category") or "General",
        difficulty=get_text(data, "difficulty") or "easy",
    )
    db.session.add(quiz)

    for q in questions:
        options = [get_text(q, "option_" + letter) for letter in "abcd"]
        db.session.add(Question(
            quiz=quiz,
            text=get_text(q, "text"),
            option_a=options[0],
            option_b=options[1],
            option_c=options[2],
            option_d=options[3],
            correct_option=get_text(q, "correct_option"),
        ))

    db.session.commit()
    click.echo(f"Imported '{quiz.title}' with {len(questions)} question(s) (id={quiz.id}).")