from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_log_dialog, fill_log, submit_log, field_error,
                                       unique_desc, find_logs, cleanup_logs)


def test_required_fields():
    """WS-012: the server rejects a log with no project, work date or hours and shows each field's error."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("required")
        try:
            open_hours(page)
            dialog = open_log_dialog(page, server_validation=True)
            fill_log(dialog, project=None, work_date="", hours="", desc=desc)
            submit_log(dialog)

            expect(field_error(dialog, "The project id field is required.")).to_be_visible()
            expect(field_error(dialog, "The work date field is required.")).to_be_visible()
            expect(field_error(dialog, "The hours worked field is required.")).to_be_visible()
            assert find_logs(page, desc) == []
        finally:
            cleanup_logs(page, desc)
            browser.close()
