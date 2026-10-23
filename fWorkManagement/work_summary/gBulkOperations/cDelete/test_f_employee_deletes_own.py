from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as, expect_toast
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, run_bulk,
                                            expect_dock, find_prefixed, deleted_msg, cleanup_prefixed)


def test_employee_deletes_own():
    """WS-072: an employee ticks two of their own pending comp entries and deletes them together."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            descs = [log["description"] for log in logs]
            show_entries(page, "Comp Hours", earliest(logs))
            tick(page, *descs)
            expect_dock(page, 2, approve=0, reject=0, delete=2)

            sent = run_bulk(page, "Delete")
            assert sorted(sent) == sorted(log["id"] for log in logs), sent
            expect_toast(page, deleted_msg(2))
            for desc in descs:
                expect(entry_row(page, desc)).to_have_count(0)
            assert find_prefixed(page, prefix) == []
            assert find_prefixed(admin, prefix) == []
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
