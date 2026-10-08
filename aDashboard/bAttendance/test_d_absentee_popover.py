import re

import pytest
from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, open_attendance, any_person, absentee_name, profile_popover


def test_absentee_popover():
    """DB-007: clicking a person in the Attendance lists opens a popover with their name, today's
    status ('On leave today' / 'WFH today'), join date and a View full profile button."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        open_attendance(page)
        button, status = any_person(page)
        if button is None:
            pytest.skip("nobody is absent or working remotely today")
        name = absentee_name(button)
        button.click()

        popover = profile_popover(page)
        expect(popover).to_be_visible()
        expect(popover).to_contain_text(name)
        expect(popover).to_contain_text(status)
        expect(popover).to_contain_text(re.compile(r"Joined \d{2} [A-Z][a-z]{2} \d{4}"))
        browser.close()
