from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_log_dialog, fill_log, submit_log, field_error,
                                       unique_desc, find_logs, cleanup_logs)


def test_hours_below_one():
    """WS-013: 0 and negative hours are refused with 'must be at least 1'."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("below one")
        try:
            open_hours(page)
            dialog = open_log_dialog(page, server_validation=True)
            for hours in ["0", "-2"]:
                fill_log(dialog, hours=hours, desc=desc)
                submit_log(dialog)
                expect(field_error(dialog, "The hours worked field must be at least 1.")).to_be_visible()
            assert find_logs(page, desc) == []
        finally:
            cleanup_logs(page, desc)
            browser.close()
