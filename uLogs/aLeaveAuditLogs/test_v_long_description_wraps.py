"""LAL-021: A long description is shown in full and wraps inside its column.

Steps:
1. As admin, apply a one-day LOP leave for the QA employee (AutoUser_tNuUc, id 247) far in the future.
2. Cancel it with a 300-character reason, so the "Cancelled" log carries a long description.
3. Open Leave Audit Logs filtered to the QA employee and today and find that row.

Expected: the whole description (including the long reason) is in the cell, nothing is clipped or hidden
(the text wraps instead of overflowing), the Description column stays within its max width (28rem) and the
page itself doesn't scroll sideways.

Cleanup: the leave is deleted in a finally block.
"""
import json
import random
import time
from datetime import date, datetime, timedelta
from urllib.parse import unquote

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/leave-logs"
SUBTITLE = "A complete history of all leave-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url):
    page.goto(url)
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    return page_props(page)


QA_EMPLOYEE_ID = 247          # AutoUser_tNuUc, the dedicated QA employee (Morning leave policy)
LOP_LEAVE = 57                # "Loss of pay Leave" on the Morning policy
QA_REASON = "QA leave audit log"


def api_headers(page):
    # the meta csrf token goes stale after the SPA login, the XSRF cookie doesn't
    token = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    return {"X-XSRF-TOKEN": token, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}


def free_weekdays(count):
    """Random weekdays well in the future so the QA leaves don't clash with each other or with payroll tests."""
    day = date(2027, 6, 1) + timedelta(days=random.randint(0, 300))
    days = []
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=3)
    return days


def apply_leave(page, day, tag):
    """Applies a one-day LOP leave for the QA employee as admin and returns its id, or None when refused."""
    reason = f"{QA_REASON} {tag}"
    page.request.post(f"{BASE_URL}/leave", headers=api_headers(page), max_redirects=0, multipart={
        "leaveId": "", "start_date": day.isoformat(), "end_date": day.isoformat(), "reason": reason,
        "policy_leave_type_id": str(LOP_LEAVE), "day_type": "full", "start_half_session": "",
        "end_half_session": "", "supporting_document": "", "user_id": str(QA_EMPLOYEE_ID), "user_ids": "",
        "shift": "morning", "is_short_notice": "0"})
    page.goto(f"{BASE_URL}/leave/manageRequests?status=pending")
    rows = page_props(page)["leaveRequests"]["data"]
    created = [r for r in rows if r["user_id"] == QA_EMPLOYEE_ID and r["reason"] == reason]
    return created[0]["id"] if created else None


def set_leave_status(page, leave_id, status, reason=QA_REASON):
    response = page.request.patch(f"{BASE_URL}/leave/{leave_id}/status", data={"status": status, "action_reason": reason},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"setting leave {leave_id} to {status} failed: {response.status}"


def cancel_leave(page, leave_id, reason=QA_REASON):
    response = page.request.fetch(f"{BASE_URL}/leave/{leave_id}/cancel", method="DELETE",
                                  data={"status": "cancel", "action_reason": reason},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"cancelling leave {leave_id} failed: {response.status}"


def delete_leave(page, leave_id):
    return page.request.delete(f"{BASE_URL}/leave/{leave_id}", headers=api_headers(page), max_redirects=0)


def employee_logs_today(page):
    today = date.today().isoformat()
    return props_at(page, f"{LOGS_URL}?employee_id={QA_EMPLOYEE_ID}&from_date={today}&to_date={today}")["logs"]["data"]


def logs_for_leave(page, leave_id):
    """The QA employee's audit log entries for one leave, oldest first."""
    today = date.today().isoformat()
    props = props_at(page, f"{LOGS_URL}?employee_id={QA_EMPLOYEE_ID}&from_date={today}&to_date={today}")
    return sorted([log for log in props["logs"]["data"] if log["leave_application_id"] == leave_id], key=lambda l: l["id"])


LONG_REASON = ("LAL-021 long reason " + "lorem ipsum dolor sit amet consectetur " * 8).strip()[:300]


def test_lal_021_long_description_wraps():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.goto(f"{BASE_URL}/leave/dashboard")
        leave_id = None
        try:
            leave_id = apply_leave(page, free_weekdays(1)[0], "LAL-021")
            assert leave_id, "the QA leave was refused"
            cancel_leave(page, leave_id, LONG_REASON)
            time.sleep(2)

            logs = logs_for_leave(page, leave_id)
            cancelled = [l for l in logs if l["action"] == "cancelled"]
            assert cancelled, f"no cancelled log for leave {leave_id}: {[l['action'] for l in logs]}"
            description = cancelled[0]["description"]
            assert LONG_REASON in description, f"the reason is missing from {description!r}"

            cell = page.locator("table tbody tr td:nth-child(5)").filter(has_text=LONG_REASON[:40]).first
            expect(cell).to_be_visible()
            text = cell.locator("p").first
            assert text.inner_text().strip() == description, "the description is cut short"
            sizes = text.evaluate("e => ({sw: e.scrollWidth, cw: e.clientWidth, sh: e.scrollHeight, ch: e.clientHeight})")
            assert sizes["sw"] <= sizes["cw"] and sizes["sh"] <= sizes["ch"], f"text is clipped: {sizes}"
            assert cell.evaluate("e => e.getBoundingClientRect().width") <= 448 + 1, "the column is wider than 28rem"
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "the page scrolls sideways"
        finally:
            if leave_id:
                delete_leave(page, leave_id)
            browser.close()
