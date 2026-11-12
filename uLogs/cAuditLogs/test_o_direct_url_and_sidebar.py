"""AL-015: Opening the page by URL and the active sidebar item.

Steps:
1. Log in as admin.
2. Go straight to /audits.

Expected: the Audit Logs page loads with its table; Logs > Audit Log is shown and highlighted in the sidebar and no
other Logs item is.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


ACTIVE = "bg-slate-100"


def test_al_015_direct_url_and_sidebar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        page.goto(LOGS_URL)
        page.get_by_text(SUBTITLE).wait_for(state="visible")
        time.sleep(1)
        expect(page.get_by_role("heading", name="Audit Logs")).to_be_visible()
        expect(page.locator("table")).to_be_visible()

        link = page.get_by_test_id("sidebar-child-audit-log")
        expect(link).to_be_visible()
        assert ACTIVE in (link.get_attribute("class") or ""), "Audit Log is not highlighted in the sidebar"
        for other in ["leave-audit-logs", "work-mode-logs", "mail-log", "api-log", "log-viewer"]:
            item = page.get_by_test_id(f"sidebar-child-{other}")
            if item.count():
                assert ACTIVE not in (item.get_attribute("class") or "").split(), f"{other} is also highlighted"

        browser.close()
