import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_attendance, attendance_panel, absentee_buttons, absentee_row,
                                    absentee_name, absent_today_count)


def test_absentee_rows():
    """DB-006: each person under Absent Today shows their name, designation and leave type;
    with nobody absent the list says 'Everyone is present!'."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        open_attendance(page)
        count = absent_today_count(page)
        expect(absentee_buttons(page)).to_have_count(count)

        if count == 0:
            expect(attendance_panel(page, "Absent Today").get_by_text("Everyone is present!")).to_be_visible()
        for button in absentee_buttons(page).all():
            lines = [line.strip() for line in absentee_row(button).inner_text().split("\n") if line.strip()]
            assert absentee_name(button) in lines, f"name missing from {lines}"
            assert len(lines) >= 3, f"expected name, designation and leave type in {lines}"
            assert any(re.search(r"LEAVE", line) for line in lines), f"no leave type in {lines}"
        browser.close()
