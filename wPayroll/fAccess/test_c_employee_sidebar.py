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


EMPLOYEE_LINKS = ["/payroll/my/payslips", "/payroll/my/salary"]


def sidebar_payroll_links(page: Page):
    """Payroll hrefs in the sidebar, as paths."""
    hrefs = page.eval_on_selector_all("aside a[href], nav a[href]", "els => els.map(e => e.getAttribute('href'))")
    paths = {h.replace(BASE_URL, "").split("?")[0] for h in hrefs if h and "/payroll" in h}
    return sorted(paths)


def test_employee_sidebar():
    """PR-003: an employee (David) sees only My Payslips and My Salary."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        david = open_david(browser)

        assert sidebar_payroll_links(david) == sorted(EMPLOYEE_LINKS)

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_employee_sidebar
# Test Description:
#   PR-003: an employee (David) sees only My Payslips and My Salary.
# Test Steps:
#   1. Open a browser and sign in as David (david@iocod.com).
#   2. Read the Payroll links in the sidebar.
#   3. Confirm only My Payslips and My Salary are present.
