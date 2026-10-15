from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as, heading
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, run_bulk, bulk_api, me,
                                            find_prefixed, deleted_msg, MISSING_ERROR, cleanup_prefixed)


def test_admin_stale_selection():
    """WS-109: the admin ticks an employee's pending entry, the employee deletes it meanwhile, then the admin
    clicks Reject: the admin is told 'One of the selected time logs no longer exists.', the page keeps working
    and the entry doesn't come back."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            show_entries(admin, "Comp Hours", earliest([log]), employee=me(page)["name"])
            tick(admin, log["description"])

            assert bulk_api(page, "delete", [log["id"]], json_errors=False) == (302, {"success": deleted_msg(1)})

            assert run_bulk(admin, "Reject") == [log["id"]]
            expect(admin.get_by_text(MISSING_ERROR).first).to_be_visible()
            expect(heading(admin)).to_be_visible()
            assert find_prefixed(admin, prefix) == []
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
