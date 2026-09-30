from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_submissions_review, submission_rows


def test_search_no_match():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)

        main.get_by_placeholder("Search learner name, email...").fill("zzz-no-such-learner-qa")
        expect(main.get_by_text("No submissions match your filters.")).to_be_visible()
        expect(submission_rows(page)).to_have_count(0)

        browser.close()
