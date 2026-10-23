from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_log_dialog, fill_log, log_dialog, unique_desc,
                                       find_logs, cleanup_logs)


def test_cancel_does_not_save():
    """WS-010: closing a filled-in Log Hours dialog with Cancel or the X button saves nothing."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("cancel")
        try:
            open_hours(page)

            dialog = open_log_dialog(page)
            fill_log(dialog, hours=3, desc=desc)
            dialog.get_by_role("button", name="Cancel").click()
            expect(log_dialog(page)).to_have_count(0)

            dialog = open_log_dialog(page)
            fill_log(dialog, hours=3, desc=desc)
            # the X is the only button in the dialog's header bar
            dialog.locator("div.border-b > button").click()
            expect(log_dialog(page)).to_have_count(0)

            page.wait_for_timeout(1000)
            assert find_logs(page, desc) == []
        finally:
            cleanup_logs(page, desc)
            browser.close()
