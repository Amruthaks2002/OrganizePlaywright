from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, log_hours, open_edit, field_error, find_logs,
                                       unique_desc, cleanup_logs)


def test_edit_validation():
    """WS-021: an edit can't push the hours over 24 or leave them empty; the log keeps its old hours."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("edit invalid")
        try:
            open_hours(page)
            log_hours(page, desc, hours=2)
            open_tab(page, "Regular Hours")

            dialog = open_edit(page, desc)
            dialog.locator("form").evaluate("f => f.noValidate = true")
            update = dialog.get_by_role("button", name="Update")

            dialog.locator("input[type=number]").fill("30")
            update.click()
            expect(field_error(dialog, "Cannot exceed 24 hours.")).to_be_visible()

            dialog.locator("input[type=number]").fill("")
            update.click()
            expect(field_error(dialog, "Hours worked is required.")).to_be_visible()

            [log] = find_logs(page, desc)
            assert float(log["hours_worked"]) == 2, log
        finally:
            cleanup_logs(page, desc)
            browser.close()
