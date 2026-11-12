"""LAL-003: Opening the page by URL and the active sidebar item.

Steps:
1. Log in as admin.
2. Go straight to /leave-logs.

Expected:
- The Leave Audit Logs page loads (subtitle and table shown).
- The sidebar shows Logs > Leave Audit Logs, and it is highlighted as the active item.
- No other Logs item is highlighted.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/leave-logs"
SUBTITLE = "A complete history of all leave-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


ACTIVE = "bg-slate-100"


def test_lal_003_direct_url_and_sidebar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        page.goto(LOGS_URL)
        page.get_by_text(SUBTITLE).wait_for(state="visible")
        time.sleep(1)
        expect(page.locator("table")).to_be_visible()

        link = page.get_by_test_id("sidebar-child-leave-audit-logs")
        expect(link).to_be_visible()
        assert ACTIVE in (link.get_attribute("class") or ""), "Leave Audit Logs is not highlighted in the sidebar"

        for other in ["audit-log", "work-mode-logs", "mail-log", "api-log", "log-viewer"]:
            item = page.get_by_test_id(f"sidebar-child-{other}")
            if item.count():
                assert ACTIVE not in (item.get_attribute("class") or "").split(), f"{other} is also highlighted"

        browser.close()
