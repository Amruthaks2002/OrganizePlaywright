import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_submissions_review


def test_quiz_failures_tab():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)

        main.get_by_role("button", name="Quiz Failures Awaiting Approval").click()
        expect(page).to_have_url(re.compile(r"tab=quizzes"))
        expect(main.get_by_text("Quiz Failures Awaiting PM Approval")).to_be_visible()
        expect(main.get_by_text("Review failed attempts on Quiz 1 and Quiz 2")).to_be_visible()

        headers = [h.strip().upper() for h in main.locator("thead th").all_inner_texts()]
        for column in ["LEARNER", "MODULE / PROGRAM", "QUIZ 1 SCORE", "QUIZ 2 SCORE", "STATUS", "ACTIONS"]:
            assert column in headers, f"Expected a '{column}' column, got {headers}"

        main.get_by_role("button", name="Assignments Awaiting Review").click()
        expect(page).to_have_url(re.compile(r"tab=assignments"))
        expect(main.get_by_text("Evaluate employee submissions, assign grades, and provide feedback.")).to_be_visible()

        browser.close()
