from playwright.sync_api import sync_playwright
from utils.app_releases_helper import open_browser, open_releases, history_section, HISTORY_COLUMNS


def test_columns():
    """AR-042: History's columns are Published, Platform, Latest, Minimum, Release notes, By and Actions (the last
    one only for screen readers)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)

        headers = [t.strip() for t in history_section(page).locator("thead th").all_text_contents()]
        assert headers == HISTORY_COLUMNS, headers
        assert history_section(page).locator("thead th").last.locator(".sr-only").text_content().strip() == "Actions"

        browser.close()
