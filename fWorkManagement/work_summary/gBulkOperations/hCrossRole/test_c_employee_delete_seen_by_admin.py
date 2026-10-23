from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as, expect_toast
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, run_bulk, me,
                                            pending_hours, deleted_msg, cleanup_prefixed)


def test_employee_delete_seen_by_admin():
    """WS-101: when an employee bulk-deletes two of their pending comp entries, they're gone from the admin's
    Comp Hours too, and the employee's Pending Comp Hours card there drops by their 2 hours."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2, hours=1)
            descs = [log["description"] for log in logs]
            name = me(page)["name"]
            show_entries(admin, "Comp Hours", earliest(logs), employee=name)
            for desc in descs:
                expect(entry_row(admin, desc)).to_have_count(1)
            before = pending_hours(admin)

            show_entries(page, "Comp Hours", earliest(logs))
            tick(page, *descs)
            run_bulk(page, "Delete")
            expect_toast(page, deleted_msg(2))

            show_entries(admin, "Comp Hours", earliest(logs), employee=name)
            for desc in descs:
                expect(entry_row(admin, desc)).to_have_count(0)
            assert pending_hours(admin) == before - 2
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
