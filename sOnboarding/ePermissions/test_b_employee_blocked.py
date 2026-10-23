from playwright.sync_api import sync_playwright
from utils.onboarding_helper import open_browser_as, expect_forbidden, protected_urls


def test_employee_blocked():
    """PM-002: an employee opening any onboarding page directly gets 403 Forbidden."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "employee")

        for url in protected_urls():
            expect_forbidden(page, url)

        browser.close()
