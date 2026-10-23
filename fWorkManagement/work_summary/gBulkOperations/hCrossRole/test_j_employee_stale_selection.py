from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as, expect_toast, BADGES
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, run_bulk,
                                            bulk_api, statuses, rejected_msg, NONE_DELETED, cleanup_prefixed)


def test_employee_stale_selection():
    """WS-108: an employee ticks their pending entry, the admin rejects it meanwhile, then the employee clicks
    Delete: the server refuses ('None of the selected time logs could be deleted.'), the employee's table refreshes
    to show it Rejected, and the entry stays."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            show_entries(page, "Comp Hours", earliest([log]))
            tick(page, log["description"])

            assert bulk_api(admin, "reject", [log["id"]], json_errors=False) == (302, {"success": rejected_msg(1)})

            assert run_bulk(page, "Delete") == [log["id"]]
            expect_toast(page, NONE_DELETED)
            expect(entry_row(page, log["description"]).locator("span.rounded-full").last).to_have_text(BADGES["rejected"])
            assert statuses(admin, prefix) == {log["description"]: "rejected"}
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
