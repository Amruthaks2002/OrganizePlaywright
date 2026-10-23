from playwright.sync_api import sync_playwright
from utils.app_releases_helper import open_browser, open_releases, history_rows


def test_edit_only_current_rows():
    """AR-032: only the rows marked Current have an Edit button; older releases can't be edited."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)

        rows = history_rows(page)
        assert rows
        for row in rows:
            assert row["has_edit"] == ("Current" in row["badges"]), {k: v for k, v in row.items() if k != "row"}

        browser.close()
