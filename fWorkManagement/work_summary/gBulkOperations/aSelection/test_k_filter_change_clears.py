from datetime import timedelta
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, wait_for_logs, pick_employee, team_select, status_select, from_date,
                                       to_date, today, ADMIN_NAME)
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, expect_dock, dock,
                                            cleanup_prefixed)


def test_filter_change_clears():
    """WS-061: changing any filter - employee, status, To date, From date, team - refetches the table and
    drops the selection."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            day = earliest([log])
            # just that day's pending entries, so the new one is on page 1 without an employee filter
            show_entries(page, "Comp Hours", day, end=day, status="pending")
            changes = {
                "employee": lambda: pick_employee(page, ADMIN_NAME),
                "status": lambda: status_select(page).select_option("all"),
                "To date": lambda: to_date(page).fill(today().isoformat()),
                "From date": lambda: from_date(page).fill((day - timedelta(days=1)).isoformat()),
                "team": lambda: team_select(page).select_option(index=1),
            }
            for name, change in changes.items():
                tick(page, log["description"])
                expect_dock(page, 1)
                wait_for_logs(page, change)
                expect(dock(page), f"selection kept after changing {name}").to_have_count(0)
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
