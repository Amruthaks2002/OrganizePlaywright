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


def test_hr_sidebar():
    """PR-002: HR's sidebar has the same 10 Payroll links as the admin's."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_role(browser, "hr")

        assert sidebar_payroll_links(hr) == sorted(ADMIN_LINKS)

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_hr_sidebar
# Test Description:
#   PR-002: HR's sidebar has the same 10 Payroll links as the admin's.
# Test Steps:
#   1. Open a browser and sign in as HR through the Development Quick Login.
#   2. Read the Payroll links in the sidebar.
#   3. Confirm they are the same 10 links the admin sees.
