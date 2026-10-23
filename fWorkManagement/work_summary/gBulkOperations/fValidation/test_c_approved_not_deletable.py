from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, bulk_api, statuses, approved_msg, NONE_DELETED,
                                            NONE_REJECTED, comp_user_or_skip, open_comp_user, cleanup_prefixed)


def test_approved_not_deletable():
    """WS-085: sent straight to the server, a bulk delete or bulk reject of an approved entry is refused and
    the entry stays approved.

    Throwaway comp user only (WS_COMP_USER_EMAIL / WS_COMP_USER_PASSWORD); skips when unset."""
    credentials = comp_user_or_skip()  # before Playwright starts
    with sync_playwright() as p:
        user_browser, user = open_comp_user(p, credentials)
        admin_browser, admin = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(user, prefix, 1)
            assert bulk_api(admin, "approve", [log["id"]], json_errors=False) == (302, {"success": approved_msg(1)})

            assert bulk_api(admin, "delete", [log["id"]], json_errors=False) == (302, {"error": NONE_DELETED})
            assert bulk_api(admin, "reject", [log["id"]], json_errors=False) == (302, {"error": NONE_REJECTED})
            assert statuses(admin, prefix, employee_id=log["user_id"]) == {log["description"]: "approved"}
        finally:
            cleanup_prefixed(admin, prefix)
            admin_browser.close()
            user_browser.close()
