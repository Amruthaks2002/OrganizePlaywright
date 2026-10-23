from datetime import date, timedelta
import pytest
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, from_date, status_select, wait_for_logs,
                                       logs_api, data_rows, approve_button, reject_button, edit_button,
                                       delete_button, delete_log_api, page_props, today,
                                       ADMIN_ID, APPROVED_NOT_DELETABLE)

DAYS = 120


def test_approved_is_locked():
    """WS-033: an approved comp entry is read-only - no Approve/Reject/Edit/Delete buttons on its row, and
    the server refuses to delete it ('Cannot delete an approved compensatory entry.')."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        start = today() - timedelta(days=DAYS)
        approved = logs_api(page, "compensatory", "approved", start=start)["timeLogs"]["data"]
        if not approved:
            pytest.skip(f"no approved comp entries in the last {DAYS} days")
        # prefer one of Admin's own, so a broken server check never removes someone else's record
        log = next((a for a in approved if a["user_id"] == ADMIN_ID), approved[0])

        open_hours(page)
        open_tab(page, "Comp Hours")
        wait_for_logs(page, lambda: from_date(page).fill(start.isoformat()))
        wait_for_logs(page, lambda: status_select(page).select_option("approved"))
        assert data_rows(page)
        for tr in data_rows(page):
            for button in [approve_button(tr), reject_button(tr), edit_button(tr), delete_button(tr)]:
                expect(button).to_have_count(0)
            expect(tr.get_by_role("button")).to_have_count(tr.get_by_role("button", name="View").count())

        # the server answers a refused delete like a successful one (a redirect back) and puts the reason in the flash
        assert delete_log_api(page, log["id"]) in (302, 303)
        open_hours(page)
        assert page_props(page)["flash"]["error"] == APPROVED_NOT_DELETABLE, page_props(page)["flash"]
        still_there = logs_api(page, "compensatory", "approved", start=date.fromisoformat(log["work_date"]),
                               end=date.fromisoformat(log["work_date"]))["timeLogs"]["data"]
        assert log["id"] in [a["id"] for a in still_there], log

        browser.close()
