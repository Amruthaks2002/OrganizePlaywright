from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import open_browser, open_releases, page_props, history_select, APP_RELEASES_URL


def test_invalid_filter_ignored():
    """AR-048: an unknown platform in the URL is ignored: the filter shows All platforms and every release is
    listed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        total = page_props(page)["history"]["total"]

        open_releases(page, f"{APP_RELEASES_URL}?platform=windows")
        assert page_props(page)["filter"] is None
        expect(history_select(page)).to_have_value("all")
        assert page_props(page)["history"]["total"] == total

        browser.close()
