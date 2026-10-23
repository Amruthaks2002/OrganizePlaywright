from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import open_browser, open_releases, page_props, platform_radio, form_values, values


def test_default_platform_prefill():
    """AR-005: the form starts on Android, filled with Android's current latest, minimum and messages."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        current = page_props(page)["current"]

        expect(platform_radio(page, "android")).to_be_checked()
        expect(platform_radio(page, "ios")).not_to_be_checked()
        assert form_values(page) == values(current["android"]), form_values(page)

        browser.close()
