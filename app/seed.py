from sqlalchemy import inspect

from app import db
from app.models import Question, Quiz

# Multiple-choice: text, option A, B, C, D, correct option
# True/false: text, option A, option B, correct option
SAMPLE_QUIZZES = [
    {
        "title": "Python Basics",
        "description": "Check how well you know the basics of Python.",
        "category": "Programming",
        "difficulty": "easy",
        "questions": [
            (
                "Which keyword is used to define a function in Python?",
                "func",
                "def",
                "function",
                "define",
                "B",
            ),
            (
                "Which function shows output on the screen?",
                "show()",
                "display()",
                "print()",
                "output()",
                "C",
            ),
            ("Which symbol starts a comment in Python?", "//", "#", "/*", "--", "B"),
            ("What is the data type of 3.14?", "int", "str", "float", "bool", "C"),
            (
                "Which of these is a list?",
                "(1, 2, 3)",
                "{1, 2, 3}",
                "[1, 2, 3]",
                "<1, 2, 3>",
                "C",
            ),
            ('What does len("hello") return?', "4", "5", "6", "Error", "B"),
            (
                "Which keyword starts a loop over a sequence?",
                "for",
                "loop",
                "repeat",
                "do",
                "A",
            ),
            ("What is the result of 10 // 3?", "3.33", "4", "3", "1", "C"),
            (
                "Which function reads input from the user?",
                "get()",
                "input()",
                "read()",
                "scan()",
                "B",
            ),
            (
                "What is the file extension of a Python file?",
                ".pt",
                ".pyt",
                ".py",
                ".python",
                "C",
            ),
        ],
    },
    {
        "title": "General Knowledge",
        "description": "A mix of simple questions about the world.",
        "category": "General",
        "difficulty": "medium",
        "questions": [
            (
                "What is the capital of France?",
                "Berlin",
                "Madrid",
                "Paris",
                "Rome",
                "C",
            ),
            ("How many continents are there?", "5", "6", "7", "8", "C"),
            (
                "Which is the largest ocean?",
                "Atlantic",
                "Pacific",
                "Indian",
                "Arctic",
                "B",
            ),
            (
                "Who wrote the play Romeo and Juliet?",
                "Charles Dickens",
                "Mark Twain",
                "William Shakespeare",
                "Jane Austen",
                "C",
            ),
            (
                "Which country is known as the Land of the Rising Sun?",
                "China",
                "Japan",
                "Thailand",
                "India",
                "B",
            ),
            (
                "How many days are there in a leap year?",
                "364",
                "365",
                "366",
                "367",
                "C",
            ),
            (
                "What is the currency of the United Kingdom?",
                "Euro",
                "Dollar",
                "Pound",
                "Rupee",
                "C",
            ),
            (
                "Which planet is closest to the Sun?",
                "Venus",
                "Mercury",
                "Earth",
                "Mars",
                "B",
            ),
            (
                "In which year did India become independent?",
                "1945",
                "1947",
                "1950",
                "1952",
                "B",
            ),
            (
                "Which language has the most native speakers?",
                "English",
                "Spanish",
                "Mandarin Chinese",
                "Hindi",
                "C",
            ),
        ],
    },
    {
        "title": "Science",
        "description": "Basic questions from physics, chemistry and biology.",
        "category": "Science",
        "difficulty": "medium",
        "questions": [
            ("What is the chemical symbol for water?", "H2O", "CO2", "O2", "NaCl", "A"),
            (
                "Which gas do plants take in for photosynthesis?",
                "Oxygen",
                "Nitrogen",
                "Carbon dioxide",
                "Hydrogen",
                "C",
            ),
            (
                "What is the boiling point of water at sea level?",
                "90 C",
                "100 C",
                "110 C",
                "120 C",
                "B",
            ),
            (
                "Which organ pumps blood around the body?",
                "Liver",
                "Lungs",
                "Brain",
                "Heart",
                "D",
            ),
            (
                "What force pulls objects towards the Earth?",
                "Magnetism",
                "Friction",
                "Gravity",
                "Inertia",
                "C",
            ),
            (
                "Which planet is known as the Red Planet?",
                "Mars",
                "Jupiter",
                "Venus",
                "Saturn",
                "A",
            ),
            ("What is the chemical symbol for gold?", "Go", "Gd", "Au", "Ag", "C"),
            (
                "How many bones are there in an adult human body?",
                "186",
                "206",
                "226",
                "246",
                "B",
            ),
            (
                "What is the unit of electric current?",
                "Volt",
                "Watt",
                "Ohm",
                "Ampere",
                "D",
            ),
            (
                "Which part of the cell contains the DNA?",
                "Nucleus",
                "Membrane",
                "Cytoplasm",
                "Ribosome",
                "A",
            ),
            {
                "type": "true_false",
                "text": "The Earth revolves around the Sun.",
                "option_a": "True",
                "option_b": "False",
                "correct_option": "A",
            },
            ("What is the chemical symbol for water?",
             "H2O", "CO2", "O2", "NaCl", "A"),
            ("Which gas do plants take in for photosynthesis?",
             "Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen", "C"),
            ("What is the boiling point of water at sea level?",
             "90 C", "100 C", "110 C", "120 C", "B"),
            ("Which organ pumps blood around the body?",
             "Liver", "Lungs", "Brain", "Heart", "D"),
            ("What force pulls objects towards the Earth?",
             "Magnetism", "Friction", "Gravity", "Inertia", "C"),
            ("Which planet is known as the Red Planet?",
             "Mars", "Jupiter", "Venus", "Saturn", "A"),
            ("What is the chemical symbol for gold?",
             "Go", "Gd", "Au", "Ag", "C"),
            ("How many bones are there in an adult human body?",
             "186", "206", "226", "246", "B"),
            ("What is the unit of electric current?",
             "Volt", "Watt", "Ohm", "Ampere", "D"),
            ("Which part of the cell contains the DNA?",
             "Nucleus", "Membrane", "Cytoplasm", "Ribosome", "A"),
            ("Which vitamin is produced in the human body when exposed to sunlight?",
             "Vitamin A", "Vitamin B12", "Vitamin C", "Vitamin D", "D"),
            ("What is the smallest unit of an element that retains its chemical properties?",
             "Cell", "Atom", "Molecule", "Electron", "B"),
            ("Which part of the human eye controls the amount of light entering it?",
             "Retina", "Cornea", "Iris", "Lens", "C"),
            ("What is the speed of light in a vacuum approximately?",
             "300,000 km/s", "150,000 km/s", "30,000 km/s", "500,000 km/s", "A"),
            ("Which blood cells help the body fight infections?",
             "Red blood cells", "Platelets", "White blood cells", "Plasma", "C")
        ],
    },
]

# Optional explanations for sample questions, indexed by quiz title
# and question position (starting at 0).
SAMPLE_EXPLANATIONS = {
    "Python Basics": {
        0: "The def keyword is used to define a function in Python.",
        1: "The print() function displays output on the screen.",
        2: "The # symbol starts a single-line comment in Python.",
        3: "A number with a decimal point is represented as a float.",
        4: "Python lists use square brackets.",
    },
        "General Knowledge": {
        0: "Paris is the capital of France.",
        1: "There are seven commonly recognized continents.",
        2: "The Pacific Ocean is the largest ocean.",
        3: "William Shakespeare wrote Romeo and Juliet.",
        4: "Japan is known as the Land of the Rising Sun.",
        5: "A leap year has 366 days.",
        6: "The United Kingdom uses the Pound Sterling.",
        7: "Mercury is the closest planet to the Sun.",
        8: "India became independent on 15 August 1947.",
        9: "Mandarin Chinese has the most native speakers.",
    },

    "Science": {
        0: "Water contains two hydrogen atoms and one oxygen atom (H2O).",
        1: "Plants absorb carbon dioxide during photosynthesis.",
        2: "Water boils at approximately 100 degrees Celsius at sea level.",
        3: "The heart pumps blood throughout the body.",
        4: "Gravity attracts objects towards the Earth.",
        5: "Mars is called the Red Planet because of its reddish surface.",
        6: "Au is the chemical symbol for gold.",
        7: "A typical adult human skeleton has 206 bones.",
        8: "The ampere is the SI unit of electric current.",
        9: "The nucleus contains most of the DNA in a human cell.",
        10: "The body produces vitamin D in the skin when exposed to sunlight.",
        11: "An atom is the smallest unit of an element that retains its chemical properties.",
        12: "The iris controls the amount of light entering the eye.",
        13: "Light travels at approximately 300,000 kilometres per second in a vacuum.",
        14: "White blood cells help the body fight infections.",
    },
}

def seed_data():
    # Add the explanation column to existing databases if needed
    columns = {
        column["name"]
        for column in inspect(db.engine).get_columns("question")
    }

    if "explanation" not in columns:
        db.session.execute(
            db.text(
                "ALTER TABLE question "
                "ADD COLUMN explanation TEXT NOT NULL DEFAULT ''"
            )
        )
        db.session.commit()
    # Update explanations for questions in existing sample quizzes
    for quiz_title, explanations in SAMPLE_EXPLANATIONS.items():
        existing_quiz = Quiz.query.filter_by(title=quiz_title).first()

        if existing_quiz:
            for index, explanation in explanations.items():
                if index < len(existing_quiz.questions):
                    question = existing_quiz.questions[index]

                    if not question.explanation:
                        question.explanation = explanation

            db.session.commit()
    # Only add sample data when the database is empty
    if Quiz.query.count() > 0:
        return
    for quiz_data in SAMPLE_QUIZZES:
        quiz = Quiz(
            title=quiz_data["title"],
            description=quiz_data["description"],
            category=quiz_data["category"],
            difficulty=quiz_data["difficulty"],
        )
        db.session.add(quiz)
        for question_data in quiz_data["questions"]:
            if isinstance(question_data, dict):
                quiz.questions.append(
                    Question(
                        text=question_data["text"],
                        question_type=question_data["type"],
                        option_a=question_data["option_a"],
                        option_b=question_data["option_b"],
                        option_c=None,
                        option_d=None,
                        correct_option=question_data["correct_option"],
                    )
                )
            else:
                text, a, b, c, d, correct = question_data
                quiz.questions.append(
                    Question(
                        text=text,
                        question_type="multiple_choice",
                        option_a=a,
                        option_b=b,
                        option_c=c,
                        option_d=d,
                        correct_option=correct,
                    )
                )
    db.session.commit()
