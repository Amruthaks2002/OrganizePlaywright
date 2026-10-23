from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_progress, progress_search, progress_rows, main_content


def test_search_no_match():
    """JP-005: a search with no match shows the empty state."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page)

        progress_search(page).fill("zzqa-no-such-employee")
        expect(main_content(page).get_by_text("No employee onboarding journeys found.")).to_be_visible()
        expect(progress_rows(page)).to_have_count(0)

        browser.close()
