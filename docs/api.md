# QuizMaster API Reference

All API endpoints are prefixed with `/api` and exchange data using JSON.

Base URL when running locally: `http://127.0.0.1:5000`

---

## Table of Contents

- [Quick Reference](#quick-reference)
- [Cross-Platform curl Usage](#cross-platform-curl-usage)
  - [macOS and Linux (bash / zsh)](#macos-and-linux-bash--zsh)
  - [Windows Command Prompt (cmd.exe)](#windows-command-prompt-cmdexe)
  - [Windows PowerShell](#windows-powershell)
- [Endpoints](#endpoints)
  - [1. List Quizzes (`GET /api/quizzes`)](#1-list-quizzes-get-apiquizzes)
  - [2. Get a Quiz (`GET /api/quizzes/<id>`)](#2-get-a-quiz-get-apiquizzesid)
  - [3. Create a Quiz (`POST /api/quizzes`)](#3-create-a-quiz-post-apiquizzes)
  - [4. Add a Question (`POST /api/quizzes/<id>/questions`)](#4-add-a-question-post-apiquizzesidquestions)
  - [5. Submit Quiz Answers (`POST /api/quizzes/<id>/submit`)](#5-submit-quiz-answers-post-apiquizzesidsubmit)
  - [6. Quiz Leaderboard (`GET /api/quizzes/<id>/leaderboard`)](#6-quiz-leaderboard-get-apiquizzesidleaderboard)
  - [7. Platform Statistics (`GET /api/stats`)](#7-platform-statistics-get-apistats)
- [Submit Rate Limiting](#submit-rate-limiting)

---

## Quick Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/quizzes` | List quizzes. Optional `category` and `difficulty` filters |
| `GET` | `/api/quizzes/<id>` | Get quiz details and its questions (correct options omitted) |
| `POST` | `/api/quizzes` | Create a new quiz |
| `POST` | `/api/quizzes/<id>/questions` | Add a multiple-choice question to an existing quiz |
| `POST` | `/api/quizzes/<id>/submit` | Submit answers for a quiz attempt and calculate score |
| `GET` | `/api/quizzes/<id>/leaderboard` | Retrieve the top 10 attempts for a quiz |
| `GET` | `/api/stats` | Platform metrics (quiz counts, attempt counts, averages) |

---

## Cross-Platform curl Usage

When sending JSON request bodies via `curl`, shells interpret quotes differently. Use the appropriate format for your operating system and terminal:

### macOS and Linux (bash / zsh)
Single quotes `'...'` preserve the literal JSON string without escaping inner double quotes:
```bash
curl -X POST http://127.0.0.1:5000/api/quizzes \
  -H "Content-Type: application/json" \
  -d '{"title": "History Quiz", "category": "History", "difficulty": "medium"}'
```

### Windows Command Prompt (cmd.exe)
Command Prompt does not treat single quotes as string delimiters. Wrap the JSON payload in outer double quotes and escape every internal double quote with a backslash `\"`:
```cmd
curl -X POST http://127.0.0.1:5000/api/quizzes -H "Content-Type: application/json" -d "{\"title\": \"History Quiz\", \"category\": \"History\", \"difficulty\": \"medium\"}"
```

### Windows PowerShell
In Windows PowerShell (5.1 and earlier), `curl` is an alias for `Invoke-WebRequest`. Always invoke `curl.exe` explicitly and escape quotes with backslashes:
```powershell
curl.exe -X POST http://127.0.0.1:5000/api/quizzes -H "Content-Type: application/json" -d '{\"title\": \"History Quiz\", \"category\": \"History\", \"difficulty\": \"medium\"}'
```

---

## Endpoints

### 1. List Quizzes (`GET /api/quizzes`)

Retrieves all available quizzes ordered by ID.

#### Query Parameters (Optional)
- `category` (string): Filter quizzes by exact category (e.g. `?category=Programming`).
- `difficulty` (string): Filter by difficulty: `easy`, `medium`, or `hard` (e.g. `?difficulty=easy`).

#### Example Requests
**macOS / Linux:**
```bash
curl http://127.0.0.1:5000/api/quizzes
```
Filter by category and difficulty:
```bash
curl "http://127.0.0.1:5000/api/quizzes?category=Programming&difficulty=easy"
```

**Windows (cmd / PowerShell):**
```cmd
curl "http://127.0.0.1:5000/api/quizzes?category=Programming&difficulty=easy"
```

#### Success Response (`200 OK`)
```json
[
  {
    "category": "Programming",
    "created_at": "2026-11-20T14:00:00+00:00",
    "description": "Check how well you know the basics of Python.",
    "difficulty": "easy",
    "id": 1,
    "question_count": 10,
    "title": "Python Basics"
  },
  {
    "category": "General",
    "created_at": "2026-11-20T14:00:00+00:00",
    "description": "A mix of simple questions about the world.",
    "difficulty": "medium",
    "id": 2,
    "question_count": 10,
    "title": "General Knowledge"
  }
]
```

---

### 2. Get a Quiz (`GET /api/quizzes/<id>`)

Retrieves a single quiz and all of its questions. For security and test integrity, `correct_option` is omitted from questions.

#### Example Request
```bash
curl http://127.0.0.1:5000/api/quizzes/1
```

#### Success Response (`200 OK`)
```json
{
  "category": "Programming",
  "created_at": "2026-11-20T14:00:00+00:00",
  "description": "Check how well you know the basics of Python.",
  "difficulty": "easy",
  "id": 1,
  "question_count": 10,
  "questions": [
    {
      "id": 1,
      "option_a": "func",
      "option_b": "def",
      "option_c": "define",
      "option_d": "function",
      "text": "Which keyword is used to define a function in Python?"
    }
  ],
  "title": "Python Basics"
}
```

#### Error Response (`404 Not Found`)
```json
{
  "error": "Quiz not found"
}
```

---

### 3. Create a Quiz (`POST /api/quizzes`)

Creates a new quiz.

#### Request Body (JSON)
| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | **Yes** | Quiz title (must be unique, case-insensitive) |
| `description` | string | No | Short description (defaults to `""`) |
| `category` | string | No | Quiz category (defaults to `"General"`) |
| `difficulty` | string | No | Must be `"easy"`, `"medium"`, or `"hard"` (defaults to `"easy"`) |

#### Example Requests
**macOS / Linux:**
```bash
curl -X POST http://127.0.0.1:5000/api/quizzes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "World History",
    "description": "Test your knowledge of world history events.",
    "category": "History",
    "difficulty": "medium"
  }'
```

**Windows (cmd):**
```cmd
curl -X POST http://127.0.0.1:5000/api/quizzes -H "Content-Type: application/json" -d "{\"title\": \"World History\", \"description\": \"Test your knowledge of world history events.\", \"category\": \"History\", \"difficulty\": \"medium\"}"
```

**Windows (PowerShell):**
```powershell
curl.exe -X POST http://127.0.0.1:5000/api/quizzes -H "Content-Type: application/json" -d '{\"title\": \"World History\", \"description\": \"Test your knowledge of world history events.\", \"category\": \"History\", \"difficulty\": \"medium\"}'
```

#### Success Response (`201 Created`)
```json
{
  "category": "History",
  "created_at": "2026-11-20T14:35:12+00:00",
  "description": "Test your knowledge of world history events.",
  "difficulty": "medium",
  "id": 4,
  "question_count": 0,
  "title": "World History"
}
```

#### Error Responses (`400 Bad Request`)
- **Missing or blank title:**
  ```json
  {
    "error": "Title is required"
  }
  ```
- **Invalid difficulty value:**
  ```json
  {
    "error": "Difficulty must be easy, medium or hard"
  }
  ```
- **Duplicate title:**
  ```json
  {
    "error": "A quiz with this title already exists"
  }
  ```

---

### 4. Add a Question (`POST /api/quizzes/<id>/questions`)

Adds a 4-option multiple choice question to an existing quiz.

#### Request Body (JSON)
| Field | Type | Required | Description |
|---|---|---|---|
| `text` | string | **Yes** | The question prompt |
| `option_a` | string | **Yes** | Choice A |
| `option_b` | string | **Yes** | Choice B |
| `option_c` | string | **Yes** | Choice C |
| `option_d` | string | **Yes** | Choice D |
| `correct_option`| string | **Yes** | Correct answer letter: `"A"`, `"B"`, `"C"`, or `"D"` |

#### Example Requests
**macOS / Linux:**
```bash
curl -X POST http://127.0.0.1:5000/api/quizzes/4/questions \
  -H "Content-Type: application/json" \
  -d '{
    "text": "In which year did World War II end?",
    "option_a": "1943",
    "option_b": "1944",
    "option_c": "1945",
    "option_d": "1946",
    "correct_option": "C"
  }'
```

**Windows (cmd):**
```cmd
curl -X POST http://127.0.0.1:5000/api/quizzes/4/questions -H "Content-Type: application/json" -d "{\"text\": \"In which year did World War II end?\", \"option_a\": \"1943\", \"option_b\": \"1944\", \"option_c\": \"1945\", \"option_d\": \"1946\", \"correct_option\": \"C\"}"
```

**Windows (PowerShell):**
```powershell
curl.exe -X POST http://127.0.0.1:5000/api/quizzes/4/questions -H "Content-Type: application/json" -d '{\"text\": \"In which year did World War II end?\", \"option_a\": \"1943\", \"option_b\": \"1944\", \"option_c\": \"1945\", \"option_d\": \"1946\", \"correct_option\": \"C\"}'
```

#### Success Response (`201 Created`)
```json
{
  "id": 31,
  "option_a": "1943",
  "option_b": "1944",
  "option_c": "1945",
  "option_d": "1946",
  "text": "In which year did World War II end?"
}
```

#### Error Responses
- **Quiz does not exist (`404 Not Found`):**
  ```json
  {
    "error": "Quiz not found"
  }
  ```
- **Missing question text or missing options (`400 Bad Request`):**
  ```json
  {
    "error": "Question text and all 4 options are required"
  }
  ```
- **Invalid `correct_option` (`400 Bad Request`):**
  ```json
  {
    "error": "correct_option must be A, B, C or D"
  }
  ```

---

### 5. Submit Quiz Answers (`POST /api/quizzes/<id>/submit`)

Submits an attempt for a quiz, scores the responses, records the attempt in the database, and returns the result. This endpoint is rate limited (see [Submit Rate Limiting](#submit-rate-limiting)).

#### Request Body (JSON)
| Field | Type | Required | Description |
|---|---|---|---|
| `player_name` | string | **Yes** | Name of the person taking the quiz |
| `answers` | object | **Yes** | Key-value pairs where key is question ID (as string) and value is selected option letter (`"A"`, `"B"`, `"C"`, or `"D"`). Unanswered questions count as wrong. |
| `time_taken_seconds` | integer | No | Non-negative integer representing elapsed time (defaults to `0`) |

#### Example Requests
**macOS / Linux:**
```bash
curl -X POST http://127.0.0.1:5000/api/quizzes/1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "Asha",
    "answers": {
      "1": "B",
      "2": "C",
      "3": "B"
    },
    "time_taken_seconds": 45
  }'
```

**Windows (cmd):**
```cmd
curl -X POST http://127.0.0.1:5000/api/quizzes/1/submit -H "Content-Type: application/json" -d "{\"player_name\": \"Asha\", \"answers\": {\"1\": \"B\", \"2\": \"C\", \"3\": \"B\"}, \"time_taken_seconds\": 45}"
```

**Windows (PowerShell):**
```powershell
curl.exe -X POST http://127.0.0.1:5000/api/quizzes/1/submit -H "Content-Type: application/json" -d '{\"player_name\": \"Asha\", \"answers\": {\"1\": \"B\", \"2\": \"C\", \"3\": \"B\"}, \"time_taken_seconds\": 45}'
```

#### Success Response (`200 OK`)
```json
{
  "attempt_id": 1,
  "correct": 3,
  "quiz_id": 1,
  "score": 3,
  "time_taken_seconds": 45,
  "total_questions": 10,
  "wrong": 7
}
```

#### Error Responses
- **Quiz not found (`404 Not Found`):**
  ```json
  {
    "error": "Quiz not found"
  }
  ```
- **Quiz has no questions (`400 Bad Request`):**
  ```json
  {
    "error": "This quiz has no questions"
  }
  ```
- **Missing player name (`400 Bad Request`):**
  ```json
  {
    "error": "Player name is required"
  }
  ```
- **Invalid answers structure (`400 Bad Request`):**
  ```json
  {
    "error": "Answers must be an object like {\"1\": \"A\"}"
  }
  ```
- **Invalid time taken (`400 Bad Request`):**
  ```json
  {
    "error": "time_taken_seconds must be a positive number"
  }
  ```
- **Rate limit exceeded (`429 Too Many Requests`):**
  ```json
  {
    "error": "Too many submissions. Please try again later."
  }
  ```

---

### 6. Quiz Leaderboard (`GET /api/quizzes/<id>/leaderboard`)

Retrieves the top 10 attempts for a given quiz, ranked first by highest score and second by fastest completion time (`time_taken_seconds`).

#### Example Request
```bash
curl http://127.0.0.1:5000/api/quizzes/1/leaderboard
```

#### Success Response (`200 OK`)
```json
[
  {
    "created_at": "2026-11-20T14:15:30+00:00",
    "id": 1,
    "player_name": "Asha",
    "score": 10,
    "time_taken_seconds": 38,
    "total_questions": 10
  },
  {
    "created_at": "2026-11-20T14:20:10+00:00",
    "id": 2,
    "player_name": "Dev",
    "score": 9,
    "time_taken_seconds": 42,
    "total_questions": 10
  }
]
```

#### Error Response (`404 Not Found`)
```json
{
  "error": "Quiz not found"
}
```

---

### 7. Platform Statistics (`GET /api/stats`)

Returns aggregate statistics across the entire application, including total quizzes, total attempts, and individual quiz averages.

#### Example Request
```bash
curl http://127.0.0.1:5000/api/stats
```

#### Success Response (`200 OK`)
```json
{
  "quizzes": [
    {
      "attempts": 5,
      "average_score": 8.4,
      "quiz_id": 1,
      "title": "Python Basics"
    },
    {
      "attempts": 3,
      "average_score": 7.0,
      "quiz_id": 2,
      "title": "General Knowledge"
    },
    {
      "attempts": 0,
      "average_score": 0.0,
      "quiz_id": 3,
      "title": "Science"
    }
  ],
  "total_attempts": 8,
  "total_quizzes": 3
}
```

---

## Submit Rate Limiting

The answer submission route (`POST /api/quizzes/<id>/submit`) uses Flask-Limiter to prevent spam and denial of service.

- **Default Limit**: 10 submissions per minute per client IP address.
- **HTTP Status**: `429 Too Many Requests`
- **Response Headers**: Includes `Retry-After: <seconds>` indicating how long the client should wait before retrying.
- **Customization**: The rate limit can be configured using the `SUBMIT_RATE_LIMIT` environment variable in your `.env` file without modifying code:
  ```env
  SUBMIT_RATE_LIMIT=20 per minute
  ```

