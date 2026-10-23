from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, main_content, EMPLOYEE


def test_reporting_manager():
    """DB-002: an employee's card shows who they report to; the admin's card has no Reporting to row."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "employee")
        reporting = main_content(page).get_by_text("Reporting to", exact=True)
        expect(reporting).to_be_visible()
        expect(reporting.locator("xpath=following-sibling::*[1]")).to_have_text(EMPLOYEE["manager"])
        browser.close()

        browser, page = open_browser_as(p, "admin")
        expect(main_content(page).get_by_text("Designation", exact=True)).to_be_visible()
        expect(main_content(page).get_by_text("Reporting to", exact=True)).to_have_count(0)
        browser.close()
