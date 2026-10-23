import re

import pytest
from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, open_attendance, any_person, absentee_name


def test_view_full_profile():
    """DB-008: View full profile in the person popover opens that person's profile page."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        open_attendance(page)
        button, _ = any_person(page)
        if button is None:
            pytest.skip("nobody is absent or working remotely today")
        name = absentee_name(button)
        button.click()
        page.get_by_role("button", name="View full profile").click()

        expect(page).to_have_url(re.compile(r"/users/\d+/profile$"))
        expect(page).to_have_title(re.compile(rf"^{re.escape(name)} · Employee Profile"))
        browser.close()
