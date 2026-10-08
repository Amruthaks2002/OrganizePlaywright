import re

import pytest
from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, find_month_with, modal


def test_leave_popup():
    """DB-035: clicking a leave item opens its detail popup with type, leave name, status, duration and reason."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        event = find_month_with(page, "leave")
        if event is None:
            pytest.skip("no leaves in the next six months")
        title = event.inner_text().strip()
        event.click()

        popup = modal(page, "LEAVE REQUEST")
        expect(popup).to_contain_text(title)
        for label in ["STATUS", "DURATION", "REASON"]:
            # labels are upper-cased by CSS only, so match them case-insensitively
            expect(popup.get_by_text(re.compile(rf"^\s*{label}\s*$", re.I))).to_be_visible()
        popup.get_by_role("button", name="Close").click()
        expect(popup).to_be_hidden()
        browser.close()
