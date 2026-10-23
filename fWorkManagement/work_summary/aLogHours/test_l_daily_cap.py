from datetime import timedelta
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_log_dialog, fill_log, submit_log, field_error,
                                       log_hours, logs_api, find_logs, unique_desc, cleanup_logs, last_weekday,
                                       DAILY_CAP, DAILY_CAP_ERROR, ADMIN_ID)


def free_day(page):
    """A recent working day Admin has no hours on (so other tests' logs don't count towards the cap)."""
    day = last_weekday() - timedelta(days=3)
    for _ in range(30):
        if day.isoweekday() < 6 and not any(
                log["user_id"] == ADMIN_ID
                for comp_filter in ("regular", "compensatory")
                for log in logs_api(page, comp_filter, start=day, end=day, employee_id=ADMIN_ID)["timeLogs"]["data"]):
            return day
        day -= timedelta(days=1)
    raise AssertionError("no recent working day without Admin hours")


def test_daily_cap():
    """WS-048: one person can log at most 14 hours a day in total - a full 14 is accepted, one more hour on
    the same day is refused."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("cap")
        try:
            open_hours(page)
            day = free_day(page)
            log_hours(page, desc, hours=DAILY_CAP, work_date=day)

            dialog = open_log_dialog(page)
            fill_log(dialog, work_date=day, hours=1, desc=desc)
            submit_log(dialog)
            expect(field_error(dialog, DAILY_CAP_ERROR)).to_be_visible()
            assert [float(log["hours_worked"]) for log in find_logs(page, desc)] == [DAILY_CAP]
        finally:
            cleanup_logs(page, desc)
            browser.close()
