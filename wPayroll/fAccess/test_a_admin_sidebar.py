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


ADMIN_LINKS = ["/payroll", "/payroll/pay-runs", "/payroll/salaries", "/payroll/salary-revisions", "/payroll/components",
               "/payroll/templates", "/payroll/reports", "/payroll/settings", "/payroll/my/payslips", "/payroll/my/salary"]


def sidebar_payroll_links(page: Page):
    """Payroll hrefs in the sidebar, as paths."""
    hrefs = page.eval_on_selector_all("aside a[href], nav a[href]", "els => els.map(e => e.getAttribute('href'))")
    paths = {h.replace(BASE_URL, "").split("?")[0] for h in hrefs if h and "/payroll" in h}
    return sorted(paths)


def test_admin_sidebar():
    """PR-001: the admin's sidebar has all 10 Payroll links (Dashboard, Pay Runs, Employee Salaries, Salary Revisions,
    Salary Components, Templates, Reports, Settings, My Payslips, My Salary)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        admin = open_role(browser, "admin")

        assert sidebar_payroll_links(admin) == sorted(ADMIN_LINKS)

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_admin_sidebar
# Test Description:
#   PR-001: the admin's sidebar has all 10 Payroll links (Dashboard, Pay Runs, Employee Salaries, Salary Revisions,
#   Salary Components, Templates, Reports, Settings, My Payslips, My Salary).
# Test Steps:
#   1. Open a browser and sign in as admin through the Development Quick Login.
#   2. Read the Payroll links in the sidebar and compare them with the expected list.
#   3. Confirm exactly these 10 are present: Dashboard, Pay Runs, Employee Salaries, Salary Revisions, Salary
#      Components, Templates, Reports, Settings, My Payslips and My Salary.
