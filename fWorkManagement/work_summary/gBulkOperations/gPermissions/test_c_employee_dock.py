from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, open_browser_as
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, expect_dock,
                                            cleanup_prefixed)


def test_employee_dock():
    """WS-093: an employee ticking their own pending comp entry gets Approve (0) and Reject (0) disabled - they
    can't decide on comp requests - and Delete (1) enabled."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            show_entries(page, "Comp Hours", earliest([log]))
            tick(page, log["description"])
            expect_dock(page, 1, approve=0, reject=0, delete=1)
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
