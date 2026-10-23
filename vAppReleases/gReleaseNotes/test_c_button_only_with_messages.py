from playwright.sync_api import sync_playwright
from utils.app_releases_helper import open_browser, open_releases, page_props, history_rows


def test_button_only_with_messages():
    """AR-040: View release notes is offered when a release has either custom message, and not when both are the
    default text."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        data = page_props(page)["history"]["data"]

        rows = history_rows(page)
        assert len(rows) == len(data)
        for row, release in zip(rows, data):
            expected = bool(release["optional_message"] or release["mandatory_message"])
            assert row["has_notes"] == expected, (release, row["has_notes"])

        browser.close()
