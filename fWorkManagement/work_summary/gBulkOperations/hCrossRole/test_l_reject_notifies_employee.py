import time
from datetime import date
from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, open_browser_as, open_hours, expect_toast
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, run_bulk, me,
                                            notifications_for, mark_notifications_read, rejected_msg,
                                            REJECTED_NOTIFICATION, cleanup_prefixed)

WAIT_SECONDS = 30


def test_reject_notifies_employee():
    """WS-110: after an admin bulk-rejects two of an employee's entries, the employee gets one unread
    'Compensatory Work Rejected' notification per entry: 'Your comp-off request for <date> has been rejected'.
    Cleanup marks them read (notifications can't be deleted)."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        logs = []
        try:
            logs = create_logs(page, prefix, 2)
            show_entries(admin, "Comp Hours", earliest(logs), employee=me(page)["name"])
            tick(admin, *[log["description"] for log in logs])
            run_bulk(admin, "Reject")
            expect_toast(admin, rejected_msg(2))

            open_hours(page)
            title, kind = REJECTED_NOTIFICATION
            deadline = time.time() + WAIT_SECONDS  # notifications may come from a queue
            while True:
                received = {log["id"]: notifications_for(page, log["id"]) for log in logs}
                if all(received.values()) or time.time() > deadline:
                    break
                page.wait_for_timeout(2000)
            for log in logs:
                day = date.fromisoformat(log["work_date"][:10])
                found = [n for n in received[log["id"]] if n["data"]["type"] == kind]
                assert len(found) == 1, (log["id"], received[log["id"]])
                [n] = found
                assert n["data"]["title"] == title, n
                assert n["data"]["message"] == f"Your comp-off request for {day.strftime('%b %d, %Y')} has been rejected", n
                assert n["read_at"] is None, n
        finally:
            if logs:
                mark_notifications_read(page, {log["id"] for log in logs})
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
