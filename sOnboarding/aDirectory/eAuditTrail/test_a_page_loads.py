from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_review, main_content, history_url, review_url, history_search, history_filter,
    SUBMITTED_CANDIDATE_ID,
)


def test_page_loads():
    """AT-001: View History opens the audit trail with the candidate, their status and the log filters;
    Back to Details returns to the review."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)
        main = main_content(page)

        main.get_by_role("link", name="View History").click()
        expect(page).to_have_url(history_url(SUBMITTED_CANDIDATE_ID))
        expect(main.get_by_role("heading", name="Audit Trail History")).to_be_visible()
        expect(main.get_by_text("maju", exact=True)).to_be_visible()
        expect(main.get_by_text("Submitted", exact=True)).to_be_visible()
        expect(history_search(page)).to_be_visible()
        expect(history_filter(page, "All Logs")).to_have_value("all")
        expect(history_filter(page, "All Actions")).to_have_value("all")
        expect(main.get_by_role("button", name="Reset")).to_be_visible()

        main.get_by_role("link", name="Back to Details").click()
        expect(page).to_have_url(review_url(SUBMITTED_CANDIDATE_ID))

        browser.close()
