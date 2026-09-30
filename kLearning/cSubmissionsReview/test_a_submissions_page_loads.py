import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_submissions_review, submission_rows


def test_submissions_page_loads():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)

        expect(main.get_by_role("button", name="Assignments Awaiting Review")).to_be_visible()
        expect(main.get_by_role("button", name="Quiz Failures Awaiting Approval")).to_be_visible()
        expect(main.get_by_text("Evaluate employee submissions, assign grades, and provide feedback.")).to_be_visible()
        expect(main.get_by_placeholder("Search learner name, email...")).to_be_visible()
        expect(main.get_by_placeholder("All Programs")).to_be_visible()
        expect(main.locator("input[type=date]")).to_have_count(2)
        expect(main.get_by_role("button", name="Reset Filters")).to_be_visible()

        headers = [h.strip().upper() for h in main.locator("thead th").all_inner_texts()]
        for column in ["LEARNER", "ASSESSMENT", "SUBMITTED AT", "STATUS", "GRADE", "ACTIONS"]:
            assert column in headers, f"Expected a '{column}' column, got {headers}"
        expect(submission_rows(page).first).to_be_visible()
        expect(submission_rows(page).first.get_by_role("link", name="Grade / Review")).to_have_attribute(
            "href", re.compile(r"/admin/learning/programs/\d+/assignments/\d+/submissions/\d+$")
        )

        browser.close()
