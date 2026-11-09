import os

from playwright.sync_api import sync_playwright
from utils.learning_helper import BASE_URL


def test_logged_out_redirected():
    """PR-015: a logged-out visitor opening any Payroll page is sent to the login page."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        page = browser.new_page()

        for path in ("/payroll", "/payroll/pay-runs", "/payroll/my/payslips", "/payroll/payslips/1/download"):
            page.goto(f"{BASE_URL}{path}")
            assert "/login" in page.url or page.url.rstrip("/") == BASE_URL, f"{path} opened at {page.url}"

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_logged_out_redirected
# Test Description:
#   PR-015: a logged-out visitor opening any Payroll page is sent to the login page.
# Test Steps:
#   1. Open a browser without signing in.
#   2. Go to /payroll and confirm you end up on the login page.
#   3. Repeat for /payroll/pay-runs, /payroll/my/payslips and /payroll/payslips/1/download.
