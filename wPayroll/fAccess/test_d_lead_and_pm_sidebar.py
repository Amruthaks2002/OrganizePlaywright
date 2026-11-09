import os

from playwright.sync_api import Page, sync_playwright
from utils.learning_helper import BASE_URL, settle


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


EMPLOYEE_LINKS = ["/payroll/my/payslips", "/payroll/my/salary"]


def sidebar_payroll_links(page: Page):
    """Payroll hrefs in the sidebar, as paths."""
    hrefs = page.eval_on_selector_all("aside a[href], nav a[href]", "els => els.map(e => e.getAttribute('href'))")
    paths = {h.replace(BASE_URL, "").split("?")[0] for h in hrefs if h and "/payroll" in h}
    return sorted(paths)


def test_lead_and_pm_sidebar():
    """PR-004: the team lead and the project manager see only My Payslips and My Salary."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")

        for role in ("team-lead", "project-manager"):
            assert sidebar_payroll_links(open_role(browser, role)) == sorted(EMPLOYEE_LINKS), role

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_lead_and_pm_sidebar
# Test Description:
#   PR-004: the team lead and the project manager see only My Payslips and My Salary.
# Test Steps:
#   1. Open a browser and sign in as the team lead through the Development Quick Login.
#   2. Confirm the sidebar's Payroll links are only My Payslips and My Salary.
#   3. Sign in as the project manager in a new session and make the same check.
