from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, log_hours, open_edit, edit_dialog, row,
                                       find_logs, unique_desc, cleanup_logs)


def test_edit_cancel():
    """WS-020: changes made in Edit Time Log are thrown away when the dialog is cancelled."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("edit cancel")
        try:
            open_hours(page)
            log_hours(page, desc, hours=2)
            open_tab(page, "Regular Hours")

            dialog = open_edit(page, desc)
            dialog.locator("input[type=number]").fill("9")
            dialog.locator("textarea").fill(f"{desc} changed")
            dialog.get_by_role("button", name="Cancel").click()
            expect(edit_dialog(page)).to_have_count(0)

            expect(row(page, desc)).to_contain_text("2.00")
            [log] = find_logs(page, desc)
            assert float(log["hours_worked"]) == 2 and log["description"] == desc, log
        finally:
            cleanup_logs(page, desc)
            browser.close()
