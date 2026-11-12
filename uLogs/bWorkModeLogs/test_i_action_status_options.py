"""WM-008: Action Status dropdown options.

Steps:
1. Open Work Mode Audit Logs and click the Action Status filter.
2. Then type "cancel".

Expected:
- The dropdown lists, in order: Created, Approved, Rejected, Cancelled, Updated, Deleted.
- Typing "ed" keeps all of them, typing "cancel" narrows it to Cancelled.
"""
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


def status_box(page):
    return page.locator(".v-select").nth(1).locator("input.vs__search")


def pick_status(page, label):
    page.locator(".v-select").nth(1).locator(".vs__dropdown-toggle").click()
    box = status_box(page)
    box.fill(label)
    time.sleep(1)
    return refresh(page, lambda: page.get_by_role("option", name=label, exact=True).click())


EXPECTED = ["Created", "Approved", "Rejected", "Cancelled", "Updated", "Deleted"]


def test_wm_008_action_status_options():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_work_mode_logs(page)

        box = status_box(page)
        box.click()
        time.sleep(1)
        options = [o.strip() for o in page.get_by_role("option").all_inner_texts()]
        assert options == EXPECTED, options

        box.fill("cancel")
        time.sleep(1)
        options = [o.strip() for o in page.get_by_role("option").all_inner_texts()]
        assert options == ["Cancelled"], options

        browser.close()
