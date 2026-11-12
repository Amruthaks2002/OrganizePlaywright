"""AL-030: The Audit History address, reload and browser Back.

Steps:
1. Open Audit Logs and click View on the first row.
2. Check the address bar, reload the page.
3. Press the browser Back button once.

Expected: the address is the record's Audit History (/audits/entity?auditable_id=...&auditable_type=...), a reload
shows the same record, and one Back returns to the Audit Logs list.

Known bug: Back goes to /audits/entity without the record and still shows Audit History instead of the list.
This test fails until that's fixed.
"""
import json
import re
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


def open_audit_logs(page):
    """Logs in as admin and opens Logs > Audit Logs from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-audit-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    time.sleep(1)


def open_detail(page, row_index=0):
    """Clicks View on a row and returns the props of the Audit History it loads."""
    with page.expect_response(lambda r: "/audits/entity" in r.url) as info:
        page.locator("table tbody tr").nth(row_index).get_by_role("button", name="View").click()
    page.get_by_role("heading", name="Audit History").wait_for(state="visible")
    time.sleep(1)
    return info.value.json()["props"]


def report_cards(page):
    return page.locator("div.rounded-lg.border.overflow-hidden")


def shown(value):
    """How the detail page shows a stored value: '-' for empty."""
    return "-" if value is None or value == "" else str(value)


def test_al_030_detail_url_and_back():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_audit_logs(page)

        props = open_detail(page)
        entity = props["entity"]
        title = f"{entity['short_type']} #{entity['auditable_id']}"
        expect(page).to_have_url(re.compile(rf"/audits/entity\?.*auditable_id={entity['auditable_id']}"))

        page.reload()
        page.get_by_role("heading", name="Audit History").wait_for(state="visible")
        expect(page.get_by_text(title, exact=True)).to_be_visible()

        page.go_back()
        time.sleep(2)
        assert page.get_by_text(SUBTITLE).is_visible(), \
            f"Back went to {page.evaluate('location.href')} instead of the Audit Logs list"

        browser.close()
