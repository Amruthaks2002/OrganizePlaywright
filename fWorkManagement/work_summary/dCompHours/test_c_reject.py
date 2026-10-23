from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, show_from, log_hours, row, badge, approve_button,
                                       reject_button, edit_button, delete_button, confirm_dialog, status_select,
                                       wait_for_logs, find_logs, expect_toast, unique_desc, cleanup_logs,
                                       last_weekend_day, BADGES, REJECTED, ADMIN_NAME)


def test_reject():
    """WS-032: Reject asks for confirmation (Cancel keeps it pending); confirming marks the entry Rejected,
    removes its Approve/Reject/Edit/Delete buttons and lists it under the Rejected status filter."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("reject")
        day = last_weekend_day()
        try:
            open_hours(page)
            log_hours(page, desc, hours=2, work_date=day)
            open_tab(page, "Comp Hours")
            show_from(page, day)
            r = row(page, desc)

            reject_button(r).click()
            dialog = confirm_dialog(page)
            expect(dialog.locator("#confirm-dialog-title")).to_have_text("Reject Compensatory Hours")
            expect(dialog.locator("#confirm-dialog-message")).to_have_text(f"Reject {ADMIN_NAME}'s 2.00 compensatory hours?")
            dialog.get_by_test_id("confirm-dialog-cancel").click()
            assert badge(r) == BADGES["pending"]

            reject_button(r).click()
            confirm_dialog(page).get_by_test_id("confirm-dialog-confirm").click()
            expect_toast(page, REJECTED)
            expect(r.locator("span.rounded-full").last).to_have_text(BADGES["rejected"])
            for button in [approve_button(r), reject_button(r), edit_button(r), delete_button(r)]:
                expect(button).to_have_count(0)
            [log] = find_logs(page, desc)
            assert log["comp_off_status"] == "rejected", log

            wait_for_logs(page, lambda: status_select(page).select_option("rejected"))
            expect(row(page, desc)).to_have_count(1)
            wait_for_logs(page, lambda: status_select(page).select_option("pending"))
            expect(row(page, desc)).to_have_count(0)
        finally:
            # a rejected entry has no delete button, but the server still lets an admin delete it
            cleanup_logs(page, desc)
            browser.close()
