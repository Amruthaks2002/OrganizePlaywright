from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_submissions_review, submission_rows


def test_grade_review_page():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)

        row = submission_rows(page).first
        learner = row.locator("td").first.locator("div").first.inner_text().strip()
        assessment = row.locator("td").nth(1).locator("div").first.inner_text().strip()
        row.get_by_role("link", name="Grade / Review").click()
        page.wait_for_url("**/submissions/**")

        expect(main.get_by_text(assessment).first).to_be_visible()
        expect(main.get_by_text("Assignment Review")).to_be_visible()
        expect(main.get_by_text("Assignment Requirements")).to_be_visible()
        expect(main.get_by_text("Maximum Score")).to_be_visible()
        expect(main.get_by_text("Learner Submission")).to_be_visible()
        expect(main.get_by_text(learner).first).to_be_visible()
        expect(main.get_by_text("Grade & Feedback")).to_be_visible()
        for decision in ["Under Review", "Approved", "Rejected"]:
            expect(main.get_by_role("button", name=decision, exact=True)).to_be_visible()
        expect(main.locator("input[type=number]")).to_have_attribute("min", "0")
        expect(main.locator("input[type=number]")).to_have_attribute("max", "100")
        expect(main.get_by_placeholder("Write constructive evaluation notes here...")).to_be_visible()
        expect(main.get_by_role("button", name="Submit Review")).to_be_visible()
        expect(main.get_by_role("link", name="Back to Assignments")).to_be_visible()

        browser.close()
