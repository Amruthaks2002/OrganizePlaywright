from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as, expect_toast
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, run_bulk, me,
                                            find_prefixed, deleted_msg, cleanup_prefixed)


def test_admin_delete_seen_by_employee():
    """WS-104: when an admin bulk-deletes two of an employee's pending entries, they're gone from the employee's
    Comp Hours and the server."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            descs = [log["description"] for log in logs]
            show_entries(admin, "Comp Hours", earliest(logs), employee=me(page)["name"])
            tick(admin, *descs)
            run_bulk(admin, "Delete")
            expect_toast(admin, deleted_msg(2))

            show_entries(page, "Comp Hours", earliest(logs))
            for desc in descs:
                expect(entry_row(page, desc)).to_have_count(0)
            assert find_prefixed(page, prefix) == []
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
