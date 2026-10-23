from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, expect_dock,
                                            cleanup_prefixed)


def test_actions_per_tab():
    """WS-059: on Regular Hours the dock only offers Delete; on Comp Hours it offers Approve, Reject and Delete."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [regular] = create_logs(page, prefix, 1, comp=False)
            [comp] = create_logs(page, prefix, 1, start_index=2)

            show_entries(page, "Regular Hours", earliest([regular]), employee=ADMIN_NAME)
            tick(page, regular["description"])
            expect_dock(page, 1, approve=None, reject=None, delete=1)

            show_entries(page, "Comp Hours", earliest([comp]), employee=ADMIN_NAME)
            tick(page, comp["description"])
            expect_dock(page, 1, approve=1, reject=1, delete=1)
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
