"""API-021: "← Back to API Logs" and unknown entries.

Steps:
1. Open API Logs, open the first entry, click "← Back to API Logs".
2. Go to /api-logs/doesnotexist and /api-logs/000000000000000000000000.

Expected: Back returns to /api-logs with the list; the unknown addresses answer 404.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/api-logs"
EMPTY_MESSAGE = "No API calls match these filters."
SEARCH = "input[placeholder='User name, email or reference']"


def wait_for_list(page):
    page.get_by_role("heading", name="API Logs").wait_for(state="visible")
    time.sleep(1)


def open_api_logs(page):
    """Logs in as admin and opens Logs > API Log from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-api-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    wait_for_list(page)


def test_api_021_back_link_and_404():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_api_logs(page)

        page.locator("table tbody tr").first.locator("td").first.get_by_role("link").click()
        back = page.get_by_role("link", name="← Back to API Logs")
        back.wait_for(state="visible")
        back.click()
        wait_for_list(page)
        assert page.evaluate("location.pathname") == "/api-logs", page.evaluate("location.href")
        expect(page.locator("table")).to_be_visible()

        for log_id in ["doesnotexist", "000000000000000000000000"]:
            status = page.goto(f"{LOGS_URL}/{log_id}").status
            assert status == 404, f"/api-logs/{log_id} answered {status}"

        browser.close()
