from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, show_from, log_hours, row, badge, find_logs,
                                       cleanup_logs, unique_desc, last_weekend_day, fmt, approve_button, reject_button,
                                       edit_button, delete_button, BADGES, PROJECT, ADMIN_NAME)


def test_weekend_goes_to_comp():
    """WS-018: hours logged on a weekend become a pending compensatory request - they show under Comp Hours,
    not Regular Hours."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("weekend")
        day = last_weekend_day()
        try:
            open_hours(page)
            log_hours(page, desc, hours=3, work_date=day)

            [log] = find_logs(page, desc)
            assert log["comp_off_status"] == "pending" and log["is_weekend_or_holiday"], log
            assert log["comp_off_reason"] == "Work logged on weekend (3 hours)", log

            open_tab(page, "Regular Hours")
            show_from(page, day)
            expect(row(page, desc)).to_have_count(0)

            open_tab(page, "Comp Hours")
            show_from(page, day)
            r = row(page, desc)
            expect(r).to_have_count(1)
            for text in [ADMIN_NAME, PROJECT, fmt(day), "3.00"]:
                expect(r).to_contain_text(text)
            assert badge(r) == BADGES["pending"]
            for button in [approve_button(r), reject_button(r), edit_button(r), delete_button(r)]:
                expect(button).to_be_visible()
        finally:
            cleanup_logs(page, desc)
            browser.close()
