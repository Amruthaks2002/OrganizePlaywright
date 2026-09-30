from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_submissions_review, submission_rows


def test_reset_filters():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)

        search = main.get_by_placeholder("Search learner name, email...")
        dates = main.locator("input[type=date]")
        search.fill("zzz-no-such-learner-qa")
        dates.nth(0).fill("2026-07-01")
        dates.nth(1).fill("2026-07-31")
        expect(main.get_by_text("No submissions match your filters.")).to_be_visible()

        main.get_by_role("button", name="Reset Filters").click()
        expect(search).to_have_value("")
        expect(dates.nth(0)).to_have_value("")
        expect(dates.nth(1)).to_have_value("")
        expect(submission_rows(page).first).to_be_visible()

        browser.close()
