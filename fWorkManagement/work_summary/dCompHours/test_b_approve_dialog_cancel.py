from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, show_from, log_hours, row, badge, approve_button,
                                       reject_button, confirm_dialog, find_logs, unique_desc, cleanup_logs,
                                       last_weekend_day, BADGES, ADMIN_NAME)


def test_approve_dialog_cancel():
    """WS-031: Approve asks for confirmation naming the employee and hours; cancelling leaves the request
    pending. (Approving for real isn't tested: an approved entry can never be deleted and it changes the
    employee's comp-off balance, so it can't be cleaned up.)"""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("approve cancel")
        day = last_weekend_day()
        try:
            open_hours(page)
            log_hours(page, desc, hours=2, work_date=day)
            open_tab(page, "Comp Hours")
            show_from(page, day)

            r = row(page, desc)
            approve_button(r).click()
            dialog = confirm_dialog(page)
            expect(dialog.locator("#confirm-dialog-title")).to_have_text("Approve Compensatory Hours")
            expect(dialog.locator("#confirm-dialog-message")).to_have_text(f"Approve {ADMIN_NAME}'s 2.00 compensatory hours?")
            expect(dialog.get_by_test_id("confirm-dialog-confirm")).to_have_text("Approve")

            dialog.get_by_test_id("confirm-dialog-cancel").click()
            expect(page.get_by_test_id("confirm-dialog")).to_have_count(0)
            assert badge(r) == BADGES["pending"]
            expect(approve_button(r)).to_be_visible()
            expect(reject_button(r)).to_be_visible()
            [log] = find_logs(page, desc)
            assert log["comp_off_status"] == "pending" and log["approved_by"] is None, log
        finally:
            cleanup_logs(page, desc)
            browser.close()
