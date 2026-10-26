from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as, expect_toast
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, open_bulk,
                                            cancel_bulk, run_bulk, me, statuses, expect_dock, deleted_msg, find_prefixed,
                                            cleanup_prefixed)


def test_admin_cancel_employee_still_deletes():
    """WS-107: when the admin cancels a bulk reject, the employee's entries stay pending and the employee can
    still bulk-delete them."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            descs = [log["description"] for log in logs]
            show_entries(admin, "Comp Hours", earliest(logs), employee=me(page)["name"])
            tick(admin, *descs)
            open_bulk(admin, "Reject")
            cancel_bulk(admin)
            assert statuses(admin, prefix) == {desc: "pending" for desc in descs}

            show_entries(page, "Comp Hours", earliest(logs))
            tick(page, *descs)
            expect_dock(page, 2, approve=None, reject=None, delete=2)
            run_bulk(page, "Delete")
            expect_toast(page, deleted_msg(2))
            for desc in descs:
                expect(entry_row(page, desc)).to_have_count(0)
            assert find_prefixed(admin, prefix) == []
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
