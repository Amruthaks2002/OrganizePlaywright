from playwright.sync_api import sync_playwright
from utils.app_usage_helper import open_browser_as, expect_forbidden, SIDEBAR_LINK, APP_USAGE_URL, ACTIVITIES_URL


def test_project_manager_blocked():
    """PM-004: a project manager has no App Usage menu item and gets 403 Forbidden on App Usage and App Activity."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "project-manager")

        assert page.get_by_test_id(SIDEBAR_LINK).count() == 0
        for url in [APP_USAGE_URL, ACTIVITIES_URL]:
            expect_forbidden(page, url)

        browser.close()
