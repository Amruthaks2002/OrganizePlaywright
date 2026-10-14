from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, open_releases, page_props, history_select, history_rows,
                                       APP_RELEASES_URL)


def test_filter_from_url():
    """AR-047: opening History with ?platform=ios selects iOS in the filter and lists only iOS releases."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page, f"{APP_RELEASES_URL}?platform=ios")

        assert page_props(page)["filter"] == "ios"
        expect(history_select(page)).to_have_value("ios")
        rows = history_rows(page)
        assert rows and {r["platform"] for r in rows} == {"iOS"}, [r["platform"] for r in rows]

        browser.close()
