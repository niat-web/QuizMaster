# QuizMaster

A beginner-friendly quiz application built with Python (Flask) and JavaScript.

## Project overview

QuizMaster lets a student pick a quiz, enter a name, answer questions one at a
time and see a score. Scores are saved and shown on a leaderboard. No login is
needed.

This project is made for students who want to practice open source
contributions. The code is small and simple, and there are many small
improvements waiting to be done as issues.

## Tech used

- Python 3.11+ with Flask and Flask-SQLAlchemy
- SQLite by default, MySQL optional
- Plain HTML, CSS and JavaScript (fetch API)
- pytest for tests
- GitHub Actions to run the tests

## Requirements

- Python 3.11 or newer
- Git

## Quick start on Windows

1. Install Python from https://www.python.org/downloads/ and tick
   "Add Python to PATH" during the install.
2. Fork the repository at https://github.com/niat-web/QuizMaster (see [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines).
3. Clone your fork:

   ```
   git clone https://github.com/<your-username>/QuizMaster.git
   cd QuizMaster
   ```

4. Create and activate a virtual environment:

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

5. Install the packages:

   ```
   pip install -r requirements.txt
   ```

6. Start the app:

   ```
   python run.py
   ```

7. Open http://127.0.0.1:5000 in your browser.

The database file is created automatically on the first run, and 3 sample
quizzes are added.

## Optional: use MySQL

1. Create an empty database, for example `quizmaster`.
2. Install the MySQL driver: `pip install pymysql`
3. Copy `.env.example` to `.env` and set the connection string:

   ```
   DATABASE_URL=mysql+pymysql://username:password@localhost/quizmaster
   ```

4. Run `python run.py`. The tables are created on startup.

If `DATABASE_URL` is not set, SQLite is used.

## Running tests

```
pytest
```

The tests use an in-memory SQLite database, so your real data is not touched.

## Configuration
You can configure optional environment variables by creating a .env file based on .env.example:

FLASK_DEBUG: Set to 1 or true to enable Flask debug mode during development. It is turned off (0) by default.


## API endpoints

All endpoints are under `/api` and use JSON.

> **Looking for ready-to-run curl examples and error schemas?**  
> Check out the complete [API Documentation (docs/api.md)](docs/api.md) for curl commands (macOS, Linux, and Windows), request/response payloads, and error codes for every endpoint.

| Method | Endpoint                        | Description                                  |
|--------|---------------------------------|----------------------------------------------|
| GET    | /api/quizzes                    | List quizzes. Optional `category` and `difficulty` filters |
| GET    | /api/quizzes/<id>               | One quiz with its questions (no answers)     |
| POST   | /api/quizzes                    | Create a quiz                                |
| POST   | /api/quizzes/<id>/questions     | Add a question to a quiz                     |
| POST   | /api/quizzes/<id>/submit        | Submit answers and get the result            |
| GET    | /api/quizzes/<id>/leaderboard   | Top 10 attempts for a quiz                   |
| GET    | /api/stats                      | Total quizzes, total attempts, average score per quiz |

Example body for submitting answers (keys are question ids):

```json
{
  "player_name": "Asha",
  "answers": {"1": "B", "2": "C"},
  "time_taken_seconds": 42
}
```

Errors look like `{"error": "Quiz not found"}`.

### Submit rate limiting

`POST /api/quizzes/<id>/submit` is limited to 10 requests per minute per
client IP address. When the limit is exceeded, the API returns HTTP 429 with a
JSON error and a `Retry-After` header. The limit can be changed without
editing the route by setting `SUBMIT_RATE_LIMIT`, for example:

```
SUBMIT_RATE_LIMIT=20 per minute
```

## Troubleshooting

**Port 5000 is already in use**
Close the other program that uses the port, or change the port in `run.py`,
for example `app.run(debug=True, port=5001)`.

**The virtual environment does not activate in PowerShell**
PowerShell may block scripts. Run this once, then try again:

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Or use Command Prompt (cmd) instead of PowerShell.

**ModuleNotFoundError (for example "No module named flask")**
The virtual environment is probably not active, or the packages are not
installed. Run `venv\Scripts\activate` and then `pip install -r requirements.txt`.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before you start.

## License

MIT. See the [LICENSE](LICENSE) file.

## Screenshots

![Home page](docs/screenshots/home.jpg)

![Quiz page](docs/screenshots/quiz.jpg)

![Result page](docs/screenshots/result.jpg)

![Leaderboard](docs/screenshots/leaderboard.jpg)