"""AL-034: A real change is recorded with the right values.

Steps (as admin, for the QA employee AutoUser_tNuUc, id 247, a one-day LOP leave far in the future):
1. Apply the leave, approve it, then delete it.
2. Open that leave's Audit History, and Audit Logs filtered to LeaveApplication today.

Expected:
- Three records, oldest first: created, updated, deleted, all by Admin User and within a few minutes of now.
- created: new values hold the employee, the dates, 1 leave day and status pending.
- updated: status goes from pending to approved.
- deleted: the old values hold status approved.
- The list shows the three records for this leave id.

Cleanup: the leave is deleted as part of the test (and again in a finally block if a step fails).
"""
import json
import random
import time
from datetime import date, datetime, timedelta, timezone
from urllib.parse import unquote, urlencode
from zoneinfo import ZoneInfo

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


def table_rows(page):
    """Visible audit rows as dicts (the empty state has fewer cells and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != 7:
            continue
        rows.append({
            "id": cells.nth(0).inner_text().strip(),
            "model": cells.nth(1).inner_text().strip(),
            "event": cells.nth(2).inner_text().strip(),
            "user": cells.nth(3).inner_text().strip(),
            "timestamp": cells.nth(4).inner_text().strip(),
            "changes": cells.nth(5).inner_text().strip(),
        })
    return rows


def short(model):
    return model.split("\\")[-1]


def total_records(page):
    return int(page.get_by_text("Total Records:").locator("xpath=following-sibling::span[1]").inner_text().strip())


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    """Audit times come as '2026-11-11T06:33:43.793000Z' (list) or '2026-11-11 06:33:43' (detail), both UTC."""
    moment = datetime.fromisoformat(created_at.replace("Z", "").replace(" ", "T"))
    return moment.replace(tzinfo=timezone.utc).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a time, e.g. 11 Nov, 2026, 03:50 PM (India time)."""
    return to_ist(created_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


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


def test_al_034_leave_change_audited():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        started = datetime.now(IST)
        day = free_weekday()
        leave_id = None
        try:
            leave_id = apply_leave(page, day, f"QA audit log AL-034 {random.randint(1000, 9999)}")
            assert leave_id, "the QA leave was refused"
            set_leave_status(page, leave_id, "approved")
            response = delete_leave(page, leave_id)
            assert response.status in (200, 302, 303), f"deleting the leave failed: {response.status}"
            deleted_id, leave_id = leave_id, None

            props = entity_audits(page, "LeaveApplication", deleted_id, events=3)
            audits = list(reversed(props["audits"]))  # listed newest first; times can tie to the second
            assert [a["event"] for a in audits] == ["created", "updated", "deleted"], [a["event"] for a in audits]
            for audit in audits:
                assert audit["user"] == "Admin User", audit
                assert abs((to_ist(audit["created_at"]) - started).total_seconds()) < 600, audit["created_at"]
            created, updated, deleted = audits
            new = created["new_values"]
            assert str(new.get("user_id")) == str(QA_EMPLOYEE_ID) and new.get("status") == "pending", new
            assert new.get("start_date") == day.isoformat() and new.get("end_date") == day.isoformat(), new
            assert float(new.get("leave_days")) == 1, new
            assert (updated["old_values"] or {}).get("status") == "pending", updated
            assert (updated["new_values"] or {}).get("status") == "approved", updated
            assert (deleted["old_values"] or {}).get("status") == "approved", deleted

            today = date.today().isoformat()
            listed = props_at(page, list_url(model="App\\Models\\LeaveApplication", date_from=today, date_to=today))["audits"]["data"]
            mine = [a["event"] for a in listed if str(a["auditable_id"]) == str(deleted_id)]
            assert sorted(mine) == ["created", "deleted", "updated"], f"the list shows {mine} for leave {deleted_id}"
        finally:
            if leave_id:
                delete_leave(page, leave_id)
            browser.close()
