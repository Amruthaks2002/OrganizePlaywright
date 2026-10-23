from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import open_browser, open_app_usage, main_content, heading, APP_RELEASES_URL


def test_app_releases_button():
    """AU-008: the App Releases button opens the App Releases page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)

        main_content(page).get_by_role("link", name="App Releases").click()
        expect(page).to_have_url(APP_RELEASES_URL)
        expect(heading(page, "App Releases")).to_be_visible()

        browser.close()
