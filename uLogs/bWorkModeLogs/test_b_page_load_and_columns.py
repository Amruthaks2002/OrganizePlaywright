"""WM-001: Page heading, subtitle, filters and table columns.

Steps:
1. Log in as admin and open Logs > Work Mode Logs from the sidebar.
2. Check the page heading "Work Mode Audit Logs" and the subtitle "A complete history of all work mode-related actions."
3. Check the filter labels: Employee, Action Status, From Date, To Date, Description / Details, and the Reset button.
4. Check the table columns, in order: Timestamp, Employee, Action By, Action, Description & Details.

Expected: everything above is shown, the columns are in that order and the page lands on /work-mode-logs.
"""
import re
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/work-mode-logs"
SUBTITLE = "A complete history of all work mode-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def open_work_mode_logs(page):
    """Logs in as admin and opens Logs > Work Mode Logs from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-work-mode-logs")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    time.sleep(1)


def test_wm_001_page_load_and_columns():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_work_mode_logs(page)

        assert page.url.split("?")[0].endswith("/work-mode-logs"), page.url
        expect(page.get_by_text("Work Mode Audit Logs", exact=True).first).to_be_visible()
        expect(page.get_by_text(SUBTITLE)).to_be_visible()

        for label in ["Employee", "Action Status", "From Date", "To Date", "Description / Details"]:
            expect(page.locator("label").filter(has_text=re.compile(f"^{re.escape(label)}$"))).to_be_visible()
        expect(page.locator("input[placeholder='Search by employee...']")).to_be_visible()
        expect(page.locator("input[placeholder='Select action status...']")).to_be_visible()
        expect(page.locator("input[placeholder='Search text...']")).to_be_visible()
        expect(page.get_by_role("button", name="Reset")).to_be_visible()

        headers = [h.inner_text().strip().upper() for h in page.locator("table thead th").all()]
        assert headers == ["TIMESTAMP", "EMPLOYEE", "ACTION BY", "ACTION", "DESCRIPTION & DETAILS"], headers

        browser.close()
