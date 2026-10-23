from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, open_browser_as, expect_toast, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, run_bulk, bulk_api,
                                            expect_dock, statuses, rejected_msg, NONE_DELETED, cleanup_prefixed)


def test_hr_approve_reject_not_delete():
    """WS-091: HR may approve and reject but not delete: ticking a pending entry offers Approve (1) / Reject (1)
    but Delete (0), a bulk delete sent straight to the server is refused, and a bulk reject goes through."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, hr = open_browser_as(p, "hr")
        prefix = bulk_prefix()
        try:
            [log] = create_logs(admin, prefix, 1)
            show_entries(hr, "Comp Hours", earliest([log]), employee=ADMIN_NAME)
            tick(hr, log["description"])
            expect_dock(hr, 1, approve=1, reject=1, delete=0)

            assert bulk_api(hr, "delete", [log["id"]], json_errors=False) == (302, {"error": NONE_DELETED})
            assert statuses(admin, prefix) == {log["description"]: "pending"}

            show_entries(hr, "Comp Hours", earliest([log]), employee=ADMIN_NAME)
            tick(hr, log["description"])
            assert run_bulk(hr, "Reject") == [log["id"]]
            expect_toast(hr, rejected_msg(1))
            assert statuses(admin, prefix) == {log["description"]: "rejected"}
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
