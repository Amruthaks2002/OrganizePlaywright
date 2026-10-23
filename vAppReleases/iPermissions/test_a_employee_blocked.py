from playwright.sync_api import sync_playwright
from utils.app_releases_helper import open_browser_as, expect_forbidden, SIDEBAR_LINK, APP_RELEASES_URL


def test_employee_blocked():
    """AR-050: Employee has no App Releases menu item and gets 403 Forbidden on App Releases."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "employee")

        assert page.get_by_test_id(SIDEBAR_LINK).count() == 0
        expect_forbidden(page, APP_RELEASES_URL)

        browser.close()
