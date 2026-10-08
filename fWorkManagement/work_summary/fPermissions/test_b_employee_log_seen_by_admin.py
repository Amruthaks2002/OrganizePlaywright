from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_browser_as, open_hours, open_tab, show_from, log_hours, row,
                                       badge, approve_button, reject_button, edit_button, delete_button, unique_desc,
                                       cleanup_logs, last_weekend_day, fmt, BADGES, EMPLOYEE_NAME, PROJECT)


def test_employee_log_seen_by_admin():
    """WS-041: an employee's weekend hours become a pending comp request they can still edit or delete
    (but not approve), and an admin sees it under the employee's name with Approve/Reject."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "employee")
        admin_browser, admin = open_browser(p)
        desc = unique_desc("employee comp")
        day = last_weekend_day()
        try:
            open_hours(page)
            log_hours(page, desc, hours=4, work_date=day)
            open_tab(page, "Comp Hours")
            show_from(page, day)
            r = row(page, desc)
            for text in [EMPLOYEE_NAME, PROJECT, fmt(day), "4.00"]:
                expect(r).to_contain_text(text)
            assert badge(r) == BADGES["pending"]
            expect(edit_button(r)).to_be_visible()
            expect(delete_button(r)).to_be_visible()
            expect(approve_button(r)).to_have_count(0)
            expect(reject_button(r)).to_have_count(0)

            open_hours(admin)
            open_tab(admin, "Comp Hours")
            show_from(admin, day)
            r = row(admin, desc)
            expect(r).to_contain_text(EMPLOYEE_NAME)
            assert badge(r) == BADGES["pending"]
            expect(approve_button(r)).to_be_visible()
            expect(reject_button(r)).to_be_visible()
        finally:
            cleanup_logs(page, desc)
            admin_browser.close()
            browser.close()
