# Contributing to QuizMaster

Thank you for helping! This guide is for first-time contributors.

## Before you start

1. Find an open issue you would like to work on.
2. Comment on the issue and say you want to work on it.
3. Wait until a maintainer assigns the issue to you. Please do not start before that.
4. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

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
6. Run the tests and make sure they pass:

   ```
   pytest
   ```

7. Commit and push:

   ```
   git add .
   git commit -m "Short message about what you changed"
   git push origin fix/issue-12-short-name
   ```

8. Open a pull request on GitHub.

## Pull request rules

- One issue per pull request. Keep it small.
- Write a clear title, for example "Add search box to the quiz list".
- Link the issue in the description with `Closes #<number>`, for example `Closes #12`.
- Keep the code simple and easy to read. Follow PEP 8 for Python.

If you are stuck, ask a question in the issue. Nobody will mind.
