import pytest
from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, open_browser_as
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, bulk_api, statuses, NONE_REJECTED, NONE_APPROVED,
                                            comp_user_or_skip, open_comp_user, cleanup_prefixed)


def test_employee_cannot_reject_own():
    """WS-094: an employee sending a bulk reject for their own pending entry straight to the server is refused,
    and the entry stays pending."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            assert bulk_api(page, "reject", [log["id"]], json_errors=False) == (302, {"error": NONE_REJECTED})
            assert statuses(page, prefix) == {log["description"]: "pending"}
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()


def test_employee_cannot_approve_own():
    """WS-094: an employee sending a bulk approve for their own pending entry is refused and it stays pending.

    Runs as the throwaway comp user (WS_COMP_USER_EMAIL / WS_COMP_USER_PASSWORD) in case the server approves it
    anyway; skips when unset."""
    credentials = comp_user_or_skip()  # before Playwright starts
    with sync_playwright() as p:
        browser, page = open_comp_user(p, credentials)
        admin_browser, admin = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            if log["can"]["approve"]:
                pytest.skip("the throwaway comp user may approve comp requests, so isn't a plain employee")
            assert bulk_api(page, "approve", [log["id"]], json_errors=False) == (302, {"error": NONE_APPROVED})
            assert statuses(page, prefix) == {log["description"]: "pending"}
        finally:
            cleanup_prefixed(admin, prefix)
            admin_browser.close()
            browser.close()
