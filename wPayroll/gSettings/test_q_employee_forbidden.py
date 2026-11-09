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


def status_of(page: Page, path):
    return page.request.get(f"{BASE_URL}{path}", max_redirects=0).status


def test_employee_forbidden():
    """PR-037: an employee gets 403 on the Settings page."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")

        assert status_of(open_david(browser), "/payroll/settings") == 403

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_employee_forbidden
# Test Description:
#   PR-037: an employee gets 403 on the Settings page.
# Test Steps:
#   1. Open a browser and sign in as David (employee).
#   2. Request the Payroll Settings page.
#   3. Confirm it returns 403.
