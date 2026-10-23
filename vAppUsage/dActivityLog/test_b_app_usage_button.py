from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import open_browser, load, main_content, heading, ACTIVITIES_URL, APP_USAGE_URL


def test_app_usage_button():
    """AL-002: the App Usage button takes you back to App Usage."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)

        main_content(page).get_by_role("link", name="App Usage").click()
        expect(page).to_have_url(APP_USAGE_URL)
        expect(heading(page)).to_be_visible()

        browser.close()
