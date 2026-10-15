from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, bulk_api, statuses, rejected_msg, skipped_msg,
                                            NONE_REJECTED, NONE_APPROVED, comp_user_or_skip, open_comp_user, cleanup_prefixed)


def test_rejected_cannot_be_rejected_again():
    """WS-087: rejecting an already rejected entry is refused ('None of the selected requests could be
    rejected.'); in a list with a pending one, the pending one is rejected and the other reported as skipped."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            first, second = create_logs(page, prefix, 2)
            assert bulk_api(page, "reject", [first["id"]], json_errors=False) == (302, {"success": rejected_msg(1)})
            assert bulk_api(page, "reject", [first["id"]], json_errors=False) == (302, {"error": NONE_REJECTED})
            assert bulk_api(page, "reject", [first["id"], second["id"]], json_errors=False) == \
                (302, {"success": f"{rejected_msg(1)} {skipped_msg(1)}"})
            assert statuses(page, prefix) == {first["description"]: "rejected", second["description"]: "rejected"}
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()


def test_rejected_cannot_be_approved():
    """WS-087: approving a rejected entry is refused and it stays rejected.

    Throwaway comp user's entry only (WS_COMP_USER_EMAIL / WS_COMP_USER_PASSWORD), in case the server approves it
    anyway; skips when unset."""
    credentials = comp_user_or_skip()  # before Playwright starts
    with sync_playwright() as p:
        user_browser, user = open_comp_user(p, credentials)
        admin_browser, admin = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(user, prefix, 1)
            assert bulk_api(admin, "reject", [log["id"]], json_errors=False) == (302, {"success": rejected_msg(1)})
            assert bulk_api(admin, "approve", [log["id"]], json_errors=False) == (302, {"error": NONE_APPROVED})
            assert statuses(admin, prefix, employee_id=log["user_id"]) == {log["description"]: "rejected"}
        finally:
            cleanup_prefixed(admin, prefix)
            admin_browser.close()
            user_browser.close()
