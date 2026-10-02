from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_history, main_content, history_entries, SUBMITTED_CANDIDATE_ID


def test_no_logs():
    """AT-002: a candidate whose profile hasn't been touched by HR shows the "No logs found" empty state."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_history(page, SUBMITTED_CANDIDATE_ID)
        main = main_content(page)

        expect(main.get_by_text("No logs found")).to_be_visible()
        expect(main.get_by_text("There is no audit history matching the specified filter criteria.")).to_be_visible()
        expect(history_entries(page)).to_have_count(0)

        browser.close()
