from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, bulk_api, statuses,
                                            NONE_DELETED, NONE_REJECTED, cleanup_prefixed)


def test_project_manager_outside_scope():
    """WS-096: a project manager with no part in the admin's project doesn't see the admin's entry and can't
    reject or delete it by sending the request directly. (Approve isn't tried: if it went through it couldn't be
    undone.)"""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, pm = open_browser_as(p, "project-manager")
        prefix = bulk_prefix()
        try:
            [log] = create_logs(admin, prefix, 1)
            data = show_entries(pm, "Comp Hours", earliest([log]))
            assert log["id"] not in [l["id"] for l in data["timeLogs"]["data"]]
            expect(entry_row(pm, log["description"])).to_have_count(0)

            assert bulk_api(pm, "reject", [log["id"]], json_errors=False) == (302, {"error": NONE_REJECTED})
            assert bulk_api(pm, "delete", [log["id"]], json_errors=False) == (302, {"error": NONE_DELETED})
            assert statuses(admin, prefix) == {log["description"]: "pending"}
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
