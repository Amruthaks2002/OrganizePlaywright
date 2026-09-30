import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import settle, open_browser, main_content, open_submissions_review, submission_rows


def test_search_by_learner():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)
        rows = submission_rows(page)

        # search for the learner on the first row, by email
        email = rows.first.locator("td").first.locator("div").nth(1).inner_text().strip()
        main.get_by_placeholder("Search learner name, email...").fill(email)
        expect(page).to_have_url(re.compile(r"search="))
        settle(page)

        assert rows.count() > 0, f"Expected submissions for {email}"
        for i in range(rows.count()):
            expect(rows.nth(i).locator("td").first).to_contain_text(email)

        browser.close()
