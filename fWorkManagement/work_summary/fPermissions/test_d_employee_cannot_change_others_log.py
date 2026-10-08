from playwright.sync_api import sync_playwright
from utils.work_summary_helper import (open_browser, open_browser_as, open_hours, log_hours, find_logs, delete_log_api,
                                       update_log_api, unique_desc, cleanup_logs)


def test_employee_cannot_change_others_log():
    """WS-043: an employee can't edit or delete someone else's log, even by sending the request directly."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        desc = unique_desc("not yours")
        try:
            open_hours(admin)
            log_hours(admin, desc, hours=2)
            [log] = find_logs(admin, desc)

            open_hours(page)
            assert update_log_api(page, log, hours_worked=9, description=f"{desc} hacked") == 403
            assert delete_log_api(page, log["id"]) == 403

            [after] = find_logs(admin, desc)
            assert after["id"] == log["id"] and float(after["hours_worked"]) == 2, after
        finally:
            cleanup_logs(admin, desc)
            browser.close()
            admin_browser.close()
