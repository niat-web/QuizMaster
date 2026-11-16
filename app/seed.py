from app import db
from app.models import Question, Quiz

# Each question: text, option A, B, C, D, correct option
SAMPLE_QUIZZES = [
    {
        "title": "Python Basics",
        "description": "Check how well you know the basics of Python.",
        "category": "Programming",
        "difficulty": "easy",
        "questions": [
            ("Which keyword is used to define a function in Python?",
             "func", "def", "function", "define", "B"),
            ("Which function shows output on the screen?",
             "show()", "display()", "print()", "output()", "C"),
            ("Which symbol starts a comment in Python?",
             "//", "#", "/*", "--", "B"),
            ("What is the data type of 3.14?",
             "int", "str", "float", "bool", "C"),
            ("Which of these is a list?",
             "(1, 2, 3)", "{1, 2, 3}", "[1, 2, 3]", "<1, 2, 3>", "C"),
            ("What does len(\"hello\") return?",
             "4", "5", "6", "Error", "B"),
            ("Which keyword starts a loop over a sequence?",
             "for", "loop", "repeat", "do", "A"),
            ("What is the result of 10 // 3?",
             "3.33", "4", "3", "1", "C"),
            ("Which function reads input from the user?",
             "get()", "input()", "read()", "scan()", "B"),
            ("What is the file extension of a Python file?",
             ".pt", ".pyt", ".py", ".python", "C"),
        ],
    },
    {
        "title": "General Knowledge",
        "description": "A mix of simple questions about the world.",
        "category": "General",
        "difficulty": "medium",
        "questions": [
            ("What is the capital of France?",
             "Berlin", "Madrid", "Paris", "Rome", "C"),
            ("How many continents are there?",
             "5", "6", "7", "8", "C"),
            ("Which is the largest ocean?",
             "Atlantic", "Pacific", "Indian", "Arctic", "B"),
            ("Who wrote the play Romeo and Juliet?",
             "Charles Dickens", "Mark Twain", "William Shakespeare",
             "Jane Austen", "C"),
            ("Which country is known as the Land of the Rising Sun?",
             "China", "Japan", "Thailand", "India", "B"),
            ("How many days are there in a leap year?",
             "364", "365", "366", "367", "C"),
            ("What is the currency of the United Kingdom?",
             "Euro", "Dollar", "Pound", "Rupee", "C"),
            ("Which planet is closest to the Sun?",
             "Venus", "Mercury", "Earth", "Mars", "B"),
            ("In which year did India become independent?",
             "1945", "1947", "1950", "1952", "B"),
            ("Which language has the most native speakers?",
             "English", "Spanish", "Mandarin Chinese", "Hindi", "C"),
        ],
    },
    {
        "title": "Science",
        "description": "Basic questions from physics, chemistry and biology.",
        "category": "Science",
        "difficulty": "medium",
        "questions": [
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
            ("What is the powerhouse of the cell?",
             "Nucleus", "Ribosome", "Mitochondria", "Endoplasmic Reticulum", "C"),
            ("Which gas makes up the majority of Earth's atmosphere?",
             "Oxygen", "Hydrogen", "Carbon dioxide", "Nitrogen", "D"),
            ("What is the hardest natural substance on Earth?",
             "Gold", "Iron", "Diamond", "Platinum", "C"),
            ("At what temperature are Celsius and Fahrenheit scales equal?",
             "-40", "0", "32", "100", "A"),
            ("Which blood cells fight infections in the human body?",
             "Red blood cells", "White blood cells", "Platelets", "Plasma", "B"),
        ],
    },
]


def seed_data():
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
        for text, a, b, c, d, correct in quiz_data["questions"]:
            quiz.questions.append(Question(
                text=text,
                option_a=a,
                option_b=b,
                option_c=c,
                option_d=d,
                correct_option=correct,
            ))
    db.session.commit()
