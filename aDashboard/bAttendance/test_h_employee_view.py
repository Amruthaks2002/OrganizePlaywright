import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, open_attendance, attendance_stat, section, retry_if_data_changed


def test_employee_view():
    """DB-011: an employee also gets the company-wide attendance numbers and can open the Attendance page.

    This asserts current behaviour; it is assumed intended (it is shown to every role)."""
    with sync_playwright() as p:
        def same_total():
            browser, page = open_browser_as(p, "admin")
            open_attendance(page)
            admin_total = attendance_stat(page, "Total Employees")
            browser.close()

            browser, page = open_browser_as(p, "employee")
            open_attendance(page)
            assert attendance_stat(page, "Total Employees") == admin_total
            return browser, page

        browser, page = retry_if_data_changed(same_total)
        section(page, "Attendance").get_by_role("link", name="View Full Attendance").click()
        expect(page).to_have_url(re.compile(r"/attendance$"))
        browser.close()
