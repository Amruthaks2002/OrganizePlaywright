"""ML-027: "Back to Mail Activity Logs" returns to the list.

Steps:
1. Open Mail Logs and open the newest mail.
2. Click "← Back to Mail Activity Logs".

Expected: the browser is back on /mail-logs with the "Mail Logs" heading and the table. (Keeping the filters
isn't required.)
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/mail-logs"
EMPTY_MESSAGE = "No mail has been sent yet."


def wait_for_list(page):
    page.get_by_role("heading", name="Mail Logs").wait_for(state="visible")
    time.sleep(1)


def open_mail_logs(page):
    """Logs in as admin and opens Logs > Mail Log from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-mail-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    wait_for_list(page)


def test_ml_027_back_to_list():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_mail_logs(page)

        page.locator("table tbody tr").first.locator("td").nth(1).get_by_role("link").click()
        back = page.get_by_role("link", name="← Back to Mail Activity Logs")
        back.wait_for(state="visible")
        back.click()
        page.get_by_role("heading", name="Mail Logs").wait_for(state="visible")
        time.sleep(1)
        assert page.evaluate("location.pathname") == "/mail-logs", page.evaluate("location.href")
        expect(page.locator("table")).to_be_visible()
        assert page.locator("table tbody tr").count() > 0

        browser.close()
