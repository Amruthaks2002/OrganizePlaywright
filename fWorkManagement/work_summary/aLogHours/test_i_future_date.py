from datetime import timedelta
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_log_dialog, fill_log, submit_log, field_error,
                                       unique_desc, find_logs, cleanup_logs, today)


def test_future_date():
    """WS-016: hours can't be logged for a day that hasn't happened yet."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("future")
        try:
            open_hours(page)
            dialog = open_log_dialog(page, server_validation=True)
            fill_log(dialog, work_date=today() + timedelta(days=1), hours="2", desc=desc)
            submit_log(dialog)
            expect(field_error(dialog, f"The work date field must be a date before or equal to {today().isoformat()}.")).to_be_visible()
            assert find_logs(page, desc) == []
        finally:
            cleanup_logs(page, desc)
            browser.close()
