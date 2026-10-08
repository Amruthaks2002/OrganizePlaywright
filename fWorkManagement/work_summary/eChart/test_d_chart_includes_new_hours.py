from playwright.sync_api import sync_playwright
from utils.work_summary_helper import (open_browser, open_hours, wait_for_chart, log_hours, user_week_hours, unique_desc,
                                       cleanup_logs, last_weekday, HOURS_URL, ADMIN_ID)

HOURS = 3


def test_chart_includes_new_hours():
    """WS-038: newly logged hours are added to the user's bar for that week in the chart data."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("chart")
        day = last_weekday()
        try:
            before = wait_for_chart(page, lambda: open_hours(page))
            hours_before = user_week_hours(before, ADMIN_ID, day)
            assert hours_before is not None, "Admin User isn't in the chart"

            log_hours(page, desc, hours=HOURS, work_date=day)
            after = wait_for_chart(page, lambda: page.goto(HOURS_URL))
            assert user_week_hours(after, ADMIN_ID, day) == hours_before + HOURS, (hours_before, after)
        finally:
            cleanup_logs(page, desc)
            browser.close()
