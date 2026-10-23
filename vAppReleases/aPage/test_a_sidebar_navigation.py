import re
from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import open_browser, main_content, heading, SIDEBAR_LINK, APP_RELEASES_URL, SUBTITLE


def test_sidebar_navigation():
    """AR-001: the App Releases sidebar item opens the page, with its heading and subtitle, and is highlighted."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        page.get_by_test_id(SIDEBAR_LINK).click()
        page.wait_for_url(APP_RELEASES_URL)
        expect(heading(page, "App Releases")).to_be_visible()
        expect(main_content(page).get_by_text(SUBTITLE)).to_be_visible()
        expect(page.get_by_test_id(SIDEBAR_LINK)).to_have_class(re.compile(r"\bbg-slate-100\b"))

        browser.close()
