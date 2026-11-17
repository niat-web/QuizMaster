"""OpenAPI description for the QuizMaster API."""

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "QuizMaster API",
        "version": "1.0.0",
        "description": "API for listing quizzes, creating questions, submitting answers, and viewing results.",
    },
    "servers": [{"url": "/", "description": "Current QuizMaster server"}],
    "tags": [{"name": "Quizzes"}, {"name": "Results"}, {"name": "Statistics"}],
    "paths": {
        "/api/quizzes": {
            "get": {
                "tags": ["Quizzes"],
                "summary": "List quizzes",
                "parameters": [
                    {"name": "category", "in": "query", "required": False, "schema": {"type": "string"}, "example": "Science"},
                    {"name": "difficulty", "in": "query", "required": False, "schema": {"type": "string", "enum": ["easy", "medium", "hard"]}, "example": "easy"},
                ],
                "responses": {"200": {"description": "Quiz list (empty when no quizzes match).", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Quiz"}}, "example": [{"id": 1, "title": "Science Basics", "description": "A short quiz", "category": "Science", "difficulty": "easy", "question_count": 1, "created_at": "2025-01-01T12:00:00+00:00"}]}}}},
            },
            "post": {
                "tags": ["Quizzes"], "summary": "Create a quiz",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreateQuiz"}, "example": {"title": "Science Basics", "description": "A short quiz", "category": "Science", "difficulty": "easy"}}}},
                "responses": {
                    "201": {"description": "Quiz created.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Quiz"}, "example": {"id": 1, "title": "Science Basics", "description": "A short quiz", "category": "Science", "difficulty": "easy", "question_count": 0, "created_at": "2025-01-01T12:00:00+00:00"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"},
                },
            },
        },
        "/api/quizzes/{quiz_id}": {
            "parameters": [{"$ref": "#/components/parameters/QuizId"}],
            "get": {
                "tags": ["Quizzes"], "summary": "Get a quiz and its questions (answers are hidden)",
                "responses": {
                    "200": {"description": "Quiz with question choices.", "content": {"application/json": {"schema": {"allOf": [{"$ref": "#/components/schemas/Quiz"}, {"type": "object", "properties": {"questions": {"type": "array", "items": {"$ref": "#/components/schemas/Question"}}}}]}, "example": {"id": 1, "title": "Science Basics", "description": "A short quiz", "category": "Science", "difficulty": "easy", "question_count": 1, "created_at": "2025-01-01T12:00:00+00:00", "questions": [{"id": 10, "text": "Which planet is known as the Red Planet?", "option_a": "Earth", "option_b": "Mars", "option_c": "Venus", "option_d": "Jupiter"}]}}}},
                    "404": {"$ref": "#/components/responses/NotFound"},
                },
            },
        },
        "/api/quizzes/{quiz_id}/questions": {
            "parameters": [{"$ref": "#/components/parameters/QuizId"}],
            "post": {
                "tags": ["Quizzes"], "summary": "Add a question to a quiz",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreateQuestion"}, "example": {"text": "Which planet is known as the Red Planet?", "option_a": "Earth", "option_b": "Mars", "option_c": "Venus", "option_d": "Jupiter", "correct_option": "B"}}}},
                "responses": {
                    "201": {"description": "Question created (correct answer is not returned).", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Question"}, "example": {"id": 10, "quiz_id": 1, "text": "Which planet is known as the Red Planet?", "option_a": "Earth", "option_b": "Mars", "option_c": "Venus", "option_d": "Jupiter"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"}, "404": {"$ref": "#/components/responses/NotFound"},
                },
            },
        },
        "/api/quizzes/{quiz_id}/submit": {
            "parameters": [{"$ref": "#/components/parameters/QuizId"}],
            "post": {
                "tags": ["Results"], "summary": "Submit quiz answers",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SubmitQuiz"}, "example": {"player_name": "Asha", "answers": {"10": "B"}, "time_taken_seconds": 42}}}},
                "responses": {
                    "200": {"description": "Score and attempt details.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SubmissionResult"}, "example": {"attempt_id": 4, "quiz_id": 1, "score": 1, "total_questions": 1, "correct": 1, "wrong": 0, "time_taken_seconds": 42}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"}, "404": {"$ref": "#/components/responses/NotFound"},
                },
            },
        },
        "/api/quizzes/{quiz_id}/leaderboard": {
            "parameters": [{"$ref": "#/components/parameters/QuizId"}],
            "get": {
                "tags": ["Results"], "summary": "Get the top 10 attempts for a quiz",
                "responses": {
                    "200": {"description": "Attempts ordered by score descending, then time ascending.", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Attempt"}}, "example": [{"id": 4, "player_name": "Asha", "score": 1, "total_questions": 1, "time_taken_seconds": 42, "created_at": "2025-01-01T12:00:00+00:00"}]}}},
                    "404": {"$ref": "#/components/responses/NotFound"},
                },
            },
        },
        "/api/stats": {
            "get": {
                "tags": ["Statistics"], "summary": "Get quiz and attempt statistics",
                "responses": {"200": {"description": "Overall counts and per-quiz averages.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Stats"}, "example": {"total_quizzes": 1, "total_attempts": 1, "quizzes": [{"quiz_id": 1, "title": "Science Basics", "attempts": 1, "average_score": 1.0}]}}}}},
            },
        },
    },
    "components": {
        "parameters": {"QuizId": {"name": "quiz_id", "in": "path", "required": True, "description": "Quiz ID", "schema": {"type": "integer", "minimum": 1}, "example": 1}},
        "responses": {
            "BadRequest": {"description": "Invalid or missing request values.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}, "examples": {"validation": {"value": {"error": "Title is required"}}, "invalidInput": {"value": {"error": "Difficulty must be easy, medium or hard"}}, "emptyQuiz": {"value": {"error": "This quiz has no questions"}}}}}},
            "NotFound": {"description": "Quiz does not exist.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}, "example": {"error": "Quiz not found"}}}},
        },
        "schemas": {
            "Error": {"type": "object", "required": ["error"], "properties": {"error": {"type": "string"}}, "example": {"error": "Quiz not found"}},
            "Quiz": {"type": "object", "required": ["id", "title", "description", "category", "difficulty", "question_count", "created_at"], "properties": {"id": {"type": "integer", "example": 1}, "title": {"type": "string", "example": "Science Basics"}, "description": {"type": "string"}, "category": {"type": "string"}, "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]}, "question_count": {"type": "integer"}, "created_at": {"type": "string", "format": "date-time"}}},
            "CreateQuiz": {"type": "object", "required": ["title"], "properties": {"title": {"type": "string", "example": "Science Basics"}, "description": {"type": "string", "default": ""}, "category": {"type": "string", "default": "General"}, "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"], "default": "easy"}}},
            "Question": {"type": "object", "required": ["id", "text", "option_a", "option_b", "option_c", "option_d"], "properties": {"id": {"type": "integer"}, "quiz_id": {"type": "integer", "description": "Present in the response when a question is created."}, "text": {"type": "string"}, "option_a": {"type": "string"}, "option_b": {"type": "string"}, "option_c": {"type": "string"}, "option_d": {"type": "string"}}},
            "CreateQuestion": {"type": "object", "required": ["text", "option_a", "option_b", "option_c", "option_d", "correct_option"], "properties": {"text": {"type": "string"}, "option_a": {"type": "string"}, "option_b": {"type": "string"}, "option_c": {"type": "string"}, "option_d": {"type": "string"}, "correct_option": {"type": "string", "enum": ["A", "B", "C", "D"]}}},
            "SubmitQuiz": {"type": "object", "required": ["player_name", "answers"], "properties": {"player_name": {"type": "string", "example": "Asha"}, "answers": {"type": "object", "description": "Map of question IDs (as strings) to selected option letters. Omitted questions count as wrong.", "additionalProperties": {"type": "string", "enum": ["A", "B", "C", "D"]}, "example": {"10": "B"}}, "time_taken_seconds": {"type": "integer", "minimum": 0, "default": 0}}},
            "SubmissionResult": {"type": "object", "properties": {"attempt_id": {"type": "integer"}, "quiz_id": {"type": "integer"}, "score": {"type": "integer"}, "total_questions": {"type": "integer"}, "correct": {"type": "integer"}, "wrong": {"type": "integer"}, "time_taken_seconds": {"type": "integer"}}},
            "Attempt": {"type": "object", "properties": {"id": {"type": "integer"}, "player_name": {"type": "string"}, "score": {"type": "integer"}, "total_questions": {"type": "integer"}, "time_taken_seconds": {"type": "integer"}, "created_at": {"type": "string", "format": "date-time"}}},
            "Stats": {"type": "object", "properties": {"total_quizzes": {"type": "integer"}, "total_attempts": {"type": "integer"}, "quizzes": {"type": "array", "items": {"type": "object", "properties": {"quiz_id": {"type": "integer"}, "title": {"type": "string"}, "attempts": {"type": "integer"}, "average_score": {"type": "number"}}}}}},
        },
    },
}
