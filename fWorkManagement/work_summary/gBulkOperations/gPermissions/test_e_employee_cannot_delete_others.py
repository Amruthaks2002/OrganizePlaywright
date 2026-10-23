from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, open_browser_as, open_hours
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, bulk_api, statuses, NONE_DELETED, cleanup_prefixed)


def test_employee_cannot_delete_others():
    """WS-095: an employee sending a bulk delete for someone else's logs (the admin's regular and comp ones)
    is refused and they stay."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            [comp] = create_logs(admin, prefix, 1)
            [regular] = create_logs(admin, prefix, 1, comp=False, start_index=2)
            open_hours(page)
            assert bulk_api(page, "delete", [comp["id"], regular["id"]], json_errors=False) == (302, {"error": NONE_DELETED})
            assert set(statuses(admin, prefix)) == {comp["description"], regular["description"]}
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
