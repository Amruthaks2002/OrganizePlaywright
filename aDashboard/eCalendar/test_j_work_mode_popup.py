import re

import pytest
from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, find_month_with, event_date, modal, ui_date


def test_work_mode_popup():
    """DB-034: clicking a work mode item opens its detail popup with type, title, date, status,
    duration and reason."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        event = find_month_with(page, "work_mode")
        if event is None:
            pytest.skip("no work mode requests in the next six months")
        title, day = event.inner_text().strip(), event_date(event)
        event.click()

        popup = modal(page, "WORK MODE")
        expect(popup).to_contain_text(title)
        expect(popup).to_contain_text(ui_date(day))
        for label in ["STATUS", "DURATION", "REASON"]:
            # labels are upper-cased by CSS only, so match them case-insensitively
            expect(popup.get_by_text(re.compile(rf"^\s*{label}\s*$", re.I))).to_be_visible()
        popup.get_by_role("button", name="Close").click()
        expect(popup).to_be_hidden()
        browser.close()
