from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, open_browser_as
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, expect_dock,
                                            cleanup_prefixed)


def test_employee_regular_delete_only():
    """WS-100: on Regular Hours an employee's dock only offers Delete."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1, comp=False)
            show_entries(page, "Regular Hours", earliest([log]))
            tick(page, log["description"])
            expect_dock(page, 1, approve=None, reject=None, delete=1)
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
