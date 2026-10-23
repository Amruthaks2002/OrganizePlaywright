from playwright.sync_api import sync_playwright
from utils.app_releases_helper import open_browser, open_releases, page_props, platform_radio, form_values, values


def test_switch_platform():
    """AR-006: picking iOS fills the form with iOS's current release (no message -> empty), and Android again
    brings Android's back."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        current = page_props(page)["current"]

        platform_radio(page, "ios").check()
        assert form_values(page) == values(current["ios"]), form_values(page)

        platform_radio(page, "android").check()
        assert form_values(page) == values(current["android"]), form_values(page)

        browser.close()
