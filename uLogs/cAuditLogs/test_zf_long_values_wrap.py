"""AL-033: Long values on the Audit History page.

Steps:
1. As admin, apply a one-day LOP leave for the QA employee (AutoUser_tNuUc, id 247) far in the future and cancel it
   with a 300-character reason (the reason is recorded as action_reason).
2. Open that leave's Audit History.

Expected: the whole reason is shown in its report card (nothing clipped, the text wraps) and the page itself
doesn't scroll sideways (wide tables scroll inside their own box).

Cleanup: the leave is deleted in a finally block (its audit records stay, as audit logs do).
"""
import json
import random
import time
from datetime import date, timedelta
from urllib.parse import unquote, urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url, wait_for=SUBTITLE):
    page.goto(url)
    page.get_by_text(wait_for).first.wait_for(state="visible")
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def open_detail(page, row_index=0):
    """Clicks View on a row and returns the props of the Audit History it loads."""
    with page.expect_response(lambda r: "/audits/entity" in r.url) as info:
        page.locator("table tbody tr").nth(row_index).get_by_role("button", name="View").click()
    page.get_by_role("heading", name="Audit History").wait_for(state="visible")
    time.sleep(1)
    return info.value.json()["props"]


def report_cards(page):
    return page.locator("div.rounded-lg.border.overflow-hidden")


def shown(value):
    """How the detail page shows a stored value: '-' for empty."""
    return "-" if value is None or value == "" else str(value)


QA_EMPLOYEE_ID = 247          # AutoUser_tNuUc, the dedicated QA employee (Morning leave policy)
LOP_LEAVE = 57                # "Loss of pay Leave" on the Morning policy


def api_headers(page):
    # the meta csrf token goes stale after the SPA login, the XSRF cookie doesn't
    token = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    return {"X-XSRF-TOKEN": token, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}


def free_weekday():
    """A random weekday well in the future so the QA leave doesn't clash with other leaves or payroll tests."""
    day = date(2027, 6, 1) + timedelta(days=random.randint(0, 300))
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day


def apply_leave(page, day, reason):
    """Applies a one-day LOP leave for the QA employee as admin and returns its id, or None when refused."""
    page.goto(f"{BASE_URL}/leave/dashboard")
    page.request.post(f"{BASE_URL}/leave", headers=api_headers(page), max_redirects=0, multipart={
        "leaveId": "", "start_date": day.isoformat(), "end_date": day.isoformat(), "reason": reason,
        "policy_leave_type_id": str(LOP_LEAVE), "day_type": "full", "start_half_session": "",
        "end_half_session": "", "supporting_document": "", "user_id": str(QA_EMPLOYEE_ID), "user_ids": "",
        "shift": "morning", "is_short_notice": "0"})
    page.goto(f"{BASE_URL}/leave/manageRequests?status=pending")
    rows = page_props(page)["leaveRequests"]["data"]
    created = [r for r in rows if r["user_id"] == QA_EMPLOYEE_ID and r["reason"] == reason]
    return created[0]["id"] if created else None


def set_leave_status(page, leave_id, status, reason="QA audit log"):
    response = page.request.patch(f"{BASE_URL}/leave/{leave_id}/status", data={"status": status, "action_reason": reason},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"setting leave {leave_id} to {status} failed: {response.status}"


def cancel_leave(page, leave_id, reason):
    response = page.request.fetch(f"{BASE_URL}/leave/{leave_id}/cancel", method="DELETE",
                                  data={"status": "cancel", "action_reason": reason},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"cancelling leave {leave_id} failed: {response.status}"


def delete_leave(page, leave_id):
    return page.request.delete(f"{BASE_URL}/leave/{leave_id}", headers=api_headers(page), max_redirects=0)


def entity_url(model, auditable_id):
    return f"{LOGS_URL}/entity?{urlencode({'auditable_type': model, 'auditable_id': auditable_id})}"


def entity_audits(page, model, auditable_id, events, timeout=30):
    """Opens a record's Audit History, waiting until it lists the expected number of records (they are written a
    moment after the change). Returns the props."""
    deadline = time.time() + timeout
    while True:
        props = props_at(page, entity_url(model, auditable_id), wait_for="Audit History")
        if len(props["audits"]) >= events or time.time() > deadline:
            return props
        time.sleep(3)


LONG_REASON = ("AL-033 long reason " + "lorem ipsum dolor sit amet consectetur " * 8).strip()[:300]


def test_al_033_long_values_wrap():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        leave_id = None
        try:
            leave_id = apply_leave(page, free_weekday(), f"QA audit log AL-033 {random.randint(1000, 9999)}")
            assert leave_id, "the QA leave was refused"
            cancel_leave(page, leave_id, LONG_REASON)

            props = entity_audits(page, "LeaveApplication", leave_id, events=2)
            assert any((a["new_values"] or {}).get("action_reason") == LONG_REASON for a in props["audits"]), \
                f"the reason isn't recorded: {[a['event'] for a in props['audits']]}"

            card = report_cards(page).filter(has_text=LONG_REASON[:40]).first
            cell = card.locator("td").filter(has_text=LONG_REASON[:40]).last
            expect(cell).to_be_visible()
            assert cell.inner_text().strip() == LONG_REASON, "the reason is cut short"
            sizes = cell.evaluate("e => ({sw: e.scrollWidth, cw: e.clientWidth})")
            assert sizes["sw"] <= sizes["cw"], f"the reason is clipped: {sizes}"
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "the page scrolls sideways"
        finally:
            if leave_id:
                delete_leave(page, leave_id)
            browser.close()
