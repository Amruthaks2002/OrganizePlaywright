from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as, expect_toast, BADGES
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, run_bulk, me,
                                            expect_dock, rejected_msg, cleanup_prefixed)


def test_admin_reject_seen_by_employee():
    """WS-103: when an admin bulk-rejects two of an employee's entries, the employee sees them Rejected and,
    ticking them, gets Delete (0) - a rejected entry can't be removed by its owner."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            descs = [log["description"] for log in logs]
            show_entries(admin, "Comp Hours", earliest(logs), employee=me(page)["name"])
            tick(admin, *descs)
            run_bulk(admin, "Reject")
            expect_toast(admin, rejected_msg(2))

            show_entries(page, "Comp Hours", earliest(logs))
            for desc in descs:
                expect(entry_row(page, desc).locator("span.rounded-full").last).to_have_text(BADGES["rejected"])
            tick(page, *descs)
            expect_dock(page, 2, approve=0, reject=0, delete=0)
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
