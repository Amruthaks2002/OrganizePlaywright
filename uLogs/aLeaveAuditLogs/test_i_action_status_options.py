"""LAL-008: Action Status dropdown options.

Steps:
1. Open Leave Audit Logs and click the Action Status filter.
2. Then type "balance".

Expected:
- The dropdown lists, in order: Created, Approved, Rejected, Cancelled, Updated, Deleted,
  Compensatory Work Requested, Compensatory Work Approved, Compensatory Work Rejected, Balance Accrued,
  Balance Updated, Balance Adjusted, Balance Initialized, System Adjustment.
- Typing "balance" narrows it to the four Balance options.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/leave-logs"
SUBTITLE = "A complete history of all leave-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def open_leave_audit_logs(page):
    """Logs in as admin and opens Logs > Leave Audit Logs from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-leave-audit-logs")
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


EXPECTED = ["Created", "Approved", "Rejected", "Cancelled", "Updated", "Deleted",
            "Compensatory Work Requested", "Compensatory Work Approved", "Compensatory Work Rejected",
            "Balance Accrued", "Balance Updated", "Balance Adjusted", "Balance Initialized", "System Adjustment"]


def test_lal_008_action_status_options():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_leave_audit_logs(page)

        box = status_box(page)
        box.click()
        time.sleep(1)
        options = [o.strip() for o in page.get_by_role("option").all_inner_texts()]
        assert options == EXPECTED, options

        box.fill("balance")
        time.sleep(1)
        options = [o.strip() for o in page.get_by_role("option").all_inner_texts()]
        assert options == ["Balance Accrued", "Balance Updated", "Balance Adjusted", "Balance Initialized"], options

        browser.close()
