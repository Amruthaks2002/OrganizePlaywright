from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_log_dialog, fill_log, submit_log, field_error,
                                       unique_desc, find_logs, cleanup_logs)


def test_decimal_hours():
    """WS-015: hours must be a whole number - 1.5 is refused."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("decimal")
        try:
            open_hours(page)
            dialog = open_log_dialog(page, server_validation=True)
            fill_log(dialog, hours="1.5", desc=desc)
            submit_log(dialog)
            expect(field_error(dialog, "The hours worked field must be an integer.")).to_be_visible()
            assert find_logs(page, desc) == []
        finally:
            cleanup_logs(page, desc)
            browser.close()
