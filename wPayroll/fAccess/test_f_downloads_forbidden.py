import os

from playwright.sync_api import Page, sync_playwright
from utils.learning_helper import BASE_URL, settle


DAVID_EMAIL = "david@iocod.com"


def open_david(browser):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    page.goto(BASE_URL)
    page.fill("#email", DAVID_EMAIL)
    page.fill("#password", "password")
    page.get_by_test_id("sign-in-button").click()
    page.wait_for_url("**/dashboard**")
    settle(page)
    return page


DOWNLOADS = ["/payroll/reports/export?report=salary_register&year=2026&month=11", "/payroll/salaries/export",
             "/payroll/salaries/import/template", "/payroll/pay-runs/1/bank-advice", "/payroll/pay-runs/1/wps"]


def status_of(page: Page, path):
    return page.request.get(f"{BASE_URL}{path}", max_redirects=0).status


def test_downloads_forbidden():
    """PR-006: an employee gets 403 and no file on the report export, salary export, import template, bank advice and
    WPS downloads."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        david = open_david(browser)

        allowed = [path for path in DOWNLOADS if status_of(david, path) != 403]
        assert not allowed, f"downloads not refused: {allowed}"

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_downloads_forbidden
# Test Description:
#   PR-006: an employee gets 403 and no file on the report export, salary export, import template, bank advice and WPS
#   downloads.
# Test Steps:
#   1. Open a browser and sign in as David (employee).
#   2. Request the salary register export, salary export, salary import template, bank advice and WPS register URLs
#      directly.
#   3. Confirm every request returns 403, so no file is served.
