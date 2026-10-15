from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as, expect_toast
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, latest, entry_row, tick, run_bulk,
                                            find_prefixed, deleted_msg, cleanup_prefixed)


def test_admin_deletes_mixed_owners():
    """WS-105: an admin ticks one of their own entries and one of an employee's and deletes both in one go;
    both are gone for the admin and the employee."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            [own] = create_logs(admin, prefix, 1)
            [theirs] = create_logs(page, prefix, 1, start_index=2)
            logs = [own, theirs]
            # just those days' pending entries, so both are on page 1 without an employee filter
            show_entries(admin, "Comp Hours", earliest(logs), end=latest(logs), status="pending")
            tick(admin, own["description"], theirs["description"])
            sent = run_bulk(admin, "Delete")
            assert sorted(sent) == sorted([own["id"], theirs["id"]]), sent
            expect_toast(admin, deleted_msg(2))
            for log in logs:
                expect(entry_row(admin, log["description"])).to_have_count(0)
            assert find_prefixed(admin, prefix) == []

            show_entries(page, "Comp Hours", earliest(logs))
            expect(entry_row(page, theirs["description"])).to_have_count(0)
            assert find_prefixed(page, prefix) == []
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
