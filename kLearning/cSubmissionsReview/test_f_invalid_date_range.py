import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_submissions_review, submission_rows


def test_invalid_date_range():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)

        # From date later than To date
        dates = main.locator("input[type=date]")
        dates.nth(0).fill("2026-08-10")
        dates.nth(1).fill("2026-07-01")
        expect(page).to_have_url(re.compile(r"date_from=2026-08-10&date_to=2026-07-01"))

        expect(main.get_by_text("No submissions match your filters.")).to_be_visible()
        expect(submission_rows(page)).to_have_count(0)

        browser.close()
