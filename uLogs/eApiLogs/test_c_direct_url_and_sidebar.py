"""API-003: Opening the page by URL and the active sidebar item.

Steps:
1. Log in as admin.
2. Go straight to /api-logs.

Expected: the API Logs page loads; Logs > API Log is shown and highlighted in the sidebar and no other Logs item is.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/api-logs"
EMPTY_MESSAGE = "No API calls match these filters."
SEARCH = "input[placeholder='User name, email or reference']"


ACTIVE = "bg-slate-100"


def test_api_003_direct_url_and_sidebar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        page.goto(LOGS_URL)
        page.get_by_role("heading", name="API Logs").wait_for(state="visible")
        time.sleep(1)
        link = page.get_by_test_id("sidebar-child-api-log")
        expect(link).to_be_visible()
        assert ACTIVE in (link.get_attribute("class") or ""), "API Log is not highlighted in the sidebar"
        for other in ["audit-log", "leave-audit-logs", "work-mode-logs", "mail-log", "log-viewer"]:
            item = page.get_by_test_id(f"sidebar-child-{other}")
            if item.count():
                assert ACTIVE not in (item.get_attribute("class") or "").split(), f"{other} is also highlighted"

        browser.close()
