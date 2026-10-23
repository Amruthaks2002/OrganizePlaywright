from datetime import date
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as, expect_toast, chart_data, user_week_hours
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, run_bulk, me,
                                            deleted_msg, cleanup_prefixed)


def test_employee_regular_delete_seen_by_admin():
    """WS-102: when an employee bulk-deletes two regular logs, they're gone from the admin's Regular Hours and
    the admin's chart loses those hours from the employee's week."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2, comp=False, hours=1)
            descs = [log["description"] for log in logs]
            user = me(page)
            start = earliest(logs).isoformat()
            days = [date.fromisoformat(log["work_date"][:10]) for log in logs]
            chart_before = chart_data(admin, date_from=start)
            before = {day: user_week_hours(chart_before, user["id"], day) for day in days}
            show_entries(admin, "Regular Hours", earliest(logs), employee=user["name"])
            for desc in descs:
                expect(entry_row(admin, desc)).to_have_count(1)

            show_entries(page, "Regular Hours", earliest(logs))
            tick(page, *descs)
            run_bulk(page, "Delete")
            expect_toast(page, deleted_msg(2))

            show_entries(admin, "Regular Hours", earliest(logs), employee=user["name"])
            for desc in descs:
                expect(entry_row(admin, desc)).to_have_count(0)
            chart_after = chart_data(admin, date_from=start)
            for day in days:
                # each of the deleted logs was 1 hour; count the ones in the same week as `day`
                same_week = sum(1 for d in days if d.isocalendar()[:2] == day.isocalendar()[:2])
                assert user_week_hours(chart_after, user["id"], day) == before[day] - same_week, (day, before, chart_after)
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
