# Contributing to QuizMaster

Thank you for helping! This guide is for first-time contributors.

## Before you start

1. Find an open issue you would like to work on.
2. Comment on the issue and say you want to work on it.
3. Wait until a maintainer assigns the issue to you. Please do not start before that.

## Steps

1. Fork the repo using the "Fork" button on GitHub.
2. Clone your fork:

   ```
   git clone https://github.com/<your-username>/QuizMaster.git
   cd QuizMaster
   ```

3. Set up the project by following the Quick start in [README.md](README.md).
4. Create a branch named like `fix/issue-12-short-name`:

   ```
   git checkout -b fix/issue-12-short-name
   ```

5. Make your changes.
6. Run the linter and tests and make sure they pass:

   ```bash
   flake8
   pytest
   ```

7. Commit and push:

   ```
   git add .
   git commit -m "Short message about what you changed"
   git push origin fix/issue-12-short-name
   ```

8. Open a pull request on GitHub.

## Code style and linting (Flake8)

We use [Flake8](https://flake8.pycqa.org/) to check that Python code follows PEP 8 style guidelines. Running Flake8 helps catch formatting inconsistencies, syntax issues, unused imports, and overly long lines before submitting changes, keeping the codebase clean and readable.

### Installing Flake8

Flake8 is included in `requirements.txt`. When you install the project dependencies in your virtual environment, Flake8 is installed automatically:

```bash
pip install -r requirements.txt
```

You can also install it individually:

```bash
pip install flake8
```

### Running Flake8 locally

From the root directory of the project, execute:

```bash
flake8
```

### What to check before submitting a pull request

Before pushing your branch or opening a pull request:

- Run `flake8` and ensure it exits with zero errors or warnings.
- Keep line lengths within the 79-character limit configured in `.flake8`.
- Run `pytest` to verify all tests pass.

## Pull request rules

- One issue per pull request. Keep it small.
- Write a clear title, for example "Add search box to the quiz list".
- Link the issue in the description with `Closes #<number>`, for example `Closes #12`.
- Keep the code simple and easy to read. Follow PEP 8 for Python and make sure `flake8` passes without errors.

If you are stuck, ask a question in the issue. Nobody will mind.
