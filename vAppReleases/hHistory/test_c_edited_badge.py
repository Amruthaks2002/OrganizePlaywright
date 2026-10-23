from playwright.sync_api import sync_playwright
from utils.app_releases_helper import open_browser, open_releases, page_props, history_rows


def test_edited_badge():
    """AR-044: the Edited badge marks exactly the releases that were changed in place after publishing."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        data = page_props(page)["history"]["data"]

        rows = history_rows(page)
        assert len(rows) == len(data)
        for row, release in zip(rows, data):
            assert ("Edited" in row["badges"]) == release["edited"], (release, row["badges"])

        browser.close()
