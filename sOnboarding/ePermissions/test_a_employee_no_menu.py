from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser_as


def test_employee_no_menu():
    """PM-001: an employee (Quick Login > Employee) doesn't see the Onboarding menu."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "employee")

        expect(page.get_by_test_id("sidebar-navigation")).to_be_visible()
        expect(page.get_by_test_id("sidebar-parent-onboarding")).to_have_count(0)

        browser.close()
