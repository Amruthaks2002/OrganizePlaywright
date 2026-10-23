from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, bulk_api, find_prefixed, NONE_REJECTED, NONE_APPROVED,
                                            comp_user_or_skip, open_comp_user, cleanup_prefixed)


def test_regular_log_not_rejectable():
    """WS-086: a regular (working day) log sent to bulk reject is refused and gets no comp status."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1, comp=False)
            assert bulk_api(page, "reject", [log["id"]], json_errors=False) == (302, {"error": NONE_REJECTED})
            [after] = find_prefixed(page, prefix)
            assert (after["comp_off_status"], after["approved_by"]) == (log["comp_off_status"], None), after
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()


def test_regular_log_not_approvable():
    """WS-086: a regular (working day) log sent to bulk approve is refused and gets no comp status or comp-off.

    Throwaway comp user's log only (WS_COMP_USER_EMAIL / WS_COMP_USER_PASSWORD), in case the server approves it
    anyway; skips when unset."""
    credentials = comp_user_or_skip()  # before Playwright starts
    with sync_playwright() as p:
        user_browser, user = open_comp_user(p, credentials)
        admin_browser, admin = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(user, prefix, 1, comp=False)
            assert bulk_api(admin, "approve", [log["id"]], json_errors=False) == (302, {"error": NONE_APPROVED})
            [after] = find_prefixed(admin, prefix, employee_id=log["user_id"])
            assert (after["comp_off_status"], after["approved_by"]) == (log["comp_off_status"], None), after
        finally:
            cleanup_prefixed(admin, prefix)
            admin_browser.close()
            user_browser.close()
