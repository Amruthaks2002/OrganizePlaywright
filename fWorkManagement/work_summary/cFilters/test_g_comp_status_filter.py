from datetime import timedelta
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, from_date, status_select, wait_for_logs,
                                       data_rows, badge, today, LOGS_URL, BADGES)


def test_comp_status_filter():
    """WS-027: the Comp Hours Status filter only lists entries with that status, and All Status lists them all."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        open_tab(page, "Comp Hours")
        everything = wait_for_logs(page, lambda: from_date(page).fill((today() - timedelta(days=120)).isoformat()))

        totals = {}
        for status in ["pending", "approved", "rejected"]:
            with page.expect_request(lambda r: r.url.startswith(LOGS_URL)) as request:
                data = wait_for_logs(page, lambda: status_select(page).select_option(status))
            assert parse_qs(urlparse(request.value.url).query)["hours[comp_status]"] == [status]
            assert {log["comp_off_status"] for log in data["timeLogs"]["data"]} <= {status}, status
            assert {badge(tr) for tr in data_rows(page)} <= {BADGES[status]}, status
            totals[status] = data["timeLogs"]["total"]

        data = wait_for_logs(page, lambda: status_select(page).select_option("all"))
        assert data["timeLogs"]["total"] == everything["timeLogs"]["total"] == sum(totals.values()), totals
        expect(status_select(page)).to_have_value("all")

        browser.close()
