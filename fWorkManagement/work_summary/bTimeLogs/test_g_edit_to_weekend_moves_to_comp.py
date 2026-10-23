from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, show_from, log_hours, open_edit, row, badge,
                                       find_logs, expect_toast, unique_desc, cleanup_logs, last_weekend_day, fmt,
                                       BADGES, UPDATED)


def test_edit_to_weekend_moves_to_comp():
    """WS-022: moving a regular log's date onto a weekend turns it into a pending comp request."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("to weekend")
        day = last_weekend_day()
        try:
            open_hours(page)
            log_hours(page, desc, hours=2)
            open_tab(page, "Regular Hours")
            show_from(page, day)

            dialog = open_edit(page, desc)
            dialog.locator("input[type=date]").fill(day.isoformat())
            dialog.get_by_role("button", name="Update").click()
            expect_toast(page, UPDATED)
            expect(row(page, desc)).to_have_count(0)

            open_tab(page, "Comp Hours")
            show_from(page, day)
            r = row(page, desc)
            expect(r).to_contain_text(fmt(day))
            assert badge(r) == BADGES["pending"]
            [log] = find_logs(page, desc)
            assert log["comp_off_status"] == "pending" and log["work_date"] == day.isoformat(), log
        finally:
            cleanup_logs(page, desc)
            browser.close()
