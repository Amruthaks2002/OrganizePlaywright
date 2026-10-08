from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_attendance, section, section_header, absent_badge,
                                    absent_today_count)


def test_expand_collapse_and_badge():
    """DB-004: the Attendance section opens and closes, and the 'N Absent' badge matches Absent Today."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        body = section(page, "Attendance")
        expect(body.get_by_text("Total Employees")).to_be_hidden()

        open_attendance(page)
        for label in ["Total Employees", "Present Today", "On Leave", "In Office", "In Work Mode",
                      "Absent Today", "Work Mode Requests"]:
            expect(body.get_by_text(label, exact=True).first).to_be_visible()
        assert absent_badge(page) == absent_today_count(page)

        section_header(page, "Attendance").click()
        expect(body.get_by_text("Total Employees")).to_be_hidden()
        browser.close()
