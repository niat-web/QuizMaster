
from playwright.sync_api import expect


def test_complete_quiz_flow(browser, live_server, browser_app):
    # Create test data in the separate browser database.
    client = browser_app.test_client()

    quiz_response = client.post("/api/quizzes", json={
        "title": "Playwright Test Quiz",
        "difficulty": "easy",
        "category": "General",
    })

    assert quiz_response.status_code < 400
    quiz_id = quiz_response.get_json()["id"]

    # Create 10 questions.
    for number in range(1, 11):
        question_response = client.post(
            f"/api/quizzes/{quiz_id}/questions",
            json={
                "text": f"Test question {number}",
                "option_a": "Correct answer",
                "option_b": "Wrong answer 1",
                "option_c": "Wrong answer 2",
                "option_d": "Wrong answer 3",
                "correct_option": "A",
            },
        )

        assert question_response.status_code < 400

    page = browser.new_page()

    try:
        # 1. Open the home page.
        page.goto(live_server)
        expect(page.locator("body")).to_be_visible()

        # 2. Open the test quiz.
        page.locator(f'[data-quiz-id="{quiz_id}"]').click()

        expect(page.locator("#start-form")).to_be_visible()

        # 3. Enter the player's name and start the quiz.
        player_name = "Playwright Tester"

        page.locator("#player-name").fill(player_name)
        page.locator('#start-form button[type="submit"]').click()

        expect(page.locator("#question-box")).to_be_visible()

        # 4. Answer all 10 questions.
        for question_number in range(1, 11):
            expect(page.locator("#progress")).to_have_text(
                f"Question {question_number} of 10"
            )

            page.locator("#option-A").check()

            if question_number < 10:
                page.locator("#next-button").click()

        # 5. Submit the quiz on the final question.
        expect(page.locator("#submit-button")).to_be_visible()
        page.locator("#submit-button").click()

        # 6. Verify the result page.
        page.wait_for_url("**/result")

        expect(page.locator("#result-box")).to_be_visible()
        expect(page.locator("#result-name")).to_contain_text(player_name)
        expect(page.locator("#result-score")).to_contain_text("10 out of 10")
        expect(page.locator("#result-correct")).to_contain_text("10")
        expect(page.locator("#result-wrong")).to_contain_text("0")

        # 7. Open the leaderboard.
        page.locator("#leaderboard-link").click()

        page.wait_for_url(f"**/leaderboard?quiz={quiz_id}")

        expect(page.locator("#leaderboard-table")).to_be_visible()
        expect(page.locator("#leaderboard-body")).to_contain_text(player_name)

    finally:
        page.close()
