from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser_as, open_hours, open_tab, show_from, log_hours_on_free_weekday,
                                       open_edit, row, delete_in_ui, find_logs, expect_toast, unique_desc, cleanup_logs,
                                       UPDATED, EMPLOYEE_NAME)


def test_employee_edit_delete_own():
    """WS-042: an employee can edit and delete their own regular log."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "employee")
        desc = unique_desc("employee own")
        try:
            open_hours(page)
            day = log_hours_on_free_weekday(page, desc, hours=2)  # the employee may be on leave today
            open_tab(page, "Regular Hours")
            show_from(page, day)
            expect(row(page, desc)).to_contain_text(EMPLOYEE_NAME)

            dialog = open_edit(page, desc)
            dialog.locator("input[type=number]").fill("4")
            dialog.get_by_role("button", name="Update").click()
            expect_toast(page, UPDATED)
            expect(row(page, desc)).to_contain_text("4.00")

            delete_in_ui(page, desc)
            expect(row(page, desc)).to_have_count(0)
            assert find_logs(page, desc) == []
        finally:
            cleanup_logs(page, desc)
            browser.close()
