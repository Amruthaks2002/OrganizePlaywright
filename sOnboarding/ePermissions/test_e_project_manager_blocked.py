from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser_as, expect_forbidden, protected_urls


def test_project_manager_blocked():
    """PM-005: a project manager doesn't see the Onboarding menu and gets 403 on every onboarding page."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "project-manager")

        expect(page.get_by_test_id("sidebar-navigation")).to_be_visible()
        expect(page.get_by_test_id("sidebar-parent-onboarding")).to_have_count(0)
        for url in protected_urls():
            expect_forbidden(page, url)

        browser.close()
