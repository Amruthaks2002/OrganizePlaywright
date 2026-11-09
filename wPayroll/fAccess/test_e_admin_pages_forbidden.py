import os

from playwright.sync_api import Page, sync_playwright
from utils.learning_helper import BASE_URL, settle


# Dedicated QA employee for the proration tests. Its baseline is hire = relieving = 2024-01-01, which keeps it out
# of every real pay run; a test opens the dates it needs and restores the baseline afterwards.
QA_EMPLOYEE_ID = 247
DAVID_EMAIL = "david@iocod.com"


def dev_login(page: Page, role):
    page.goto(BASE_URL)
    page.get_by_test_id(f"dev-login-link-{role}").click()
    page.wait_for_url(lambda url: "/dashboard" in url or "/payroll" in url)
    settle(page)


def open_role(browser, role):
    """A page signed in through the Development Quick Login (admin, hr, project-manager, team-lead, employee)."""
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    dev_login(page, role)
    return page


def open_david(browser):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    page.goto(BASE_URL)
    page.fill("#email", DAVID_EMAIL)
    page.fill("#password", "password")
    page.get_by_test_id("sign-in-button").click()
    page.wait_for_url("**/dashboard**")
    settle(page)
    return page


ADMIN_PAGES = ["/payroll", "/payroll/pay-runs", "/payroll/pay-runs/1", "/payroll/salaries",
               f"/payroll/salaries/{QA_EMPLOYEE_ID}", f"/payroll/salaries/{QA_EMPLOYEE_ID}/assign",
               "/payroll/salary-revisions", "/payroll/components", "/payroll/templates", "/payroll/templates/create",
               "/payroll/templates/1/edit", "/payroll/reports", "/payroll/settings"]


def status_of(page: Page, path):
    return page.request.get(f"{BASE_URL}{path}", max_redirects=0).status


def test_admin_pages_forbidden():
    """PR-005: an employee, the team lead and the project manager get 403 on every admin Payroll page."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")

        for name, page in (("employee", open_david(browser)), ("team-lead", open_role(browser, "team-lead")),
                           ("project-manager", open_role(browser, "project-manager"))):
            allowed = [path for path in ADMIN_PAGES if status_of(page, path) != 403]
            assert not allowed, f"{name} isn't refused: {allowed}"

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_admin_pages_forbidden
# Test Description:
#   PR-005: an employee, the team lead and the project manager get 403 on every admin Payroll page.
# Test Steps:
#   1. Open a browser and sign in as David (employee), the team lead and the project manager in separate sessions.
#   2. As each user, request every admin Payroll page: dashboard, pay runs and a pay run's detail, salaries, an
#      employee's salary and assign pages, salary revisions, components, templates (list, create, edit), reports and
#      settings.
#   3. Confirm every request returns 403; the failure message lists any page that wasn't refused and for whom.
