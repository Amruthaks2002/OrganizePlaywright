import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_progress, progress_search, progress_rows, progress_row, settle, COMPLETED_USER


def test_search_by_email():
    """JP-004: searching by email finds the employee."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page)

        progress_search(page).fill("anjana@iocod.com")
        expect(page).to_have_url(re.compile(r"search=anjana"))
        settle(page)
        expect(progress_row(page, COMPLETED_USER)).to_have_count(1)
        expect(progress_rows(page)).to_have_count(1)

        browser.close()
